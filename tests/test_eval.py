import re
from collections import defaultdict

PATTERN = r"\w+"

THRESHOLDS = {
    "contains": 1.0,
    "similar": 0.2,
    "llm-rubrik": 0.2,
}


def keyword_overlap_scorer(*, input, output, expected_output, metadata, **kwargs):
    if metadata.get("eval") != "contains":
        return []

    output_keywords = set(re.findall(PATTERN, output.lower()))
    expected_keywords = set(re.findall(PATTERN, expected_output.lower()))
    overlap = len(expected_keywords & output_keywords) / len(expected_keywords)
    return {"name": metadata.get("eval"), "value": overlap}


def test_evals(
    langfuse,
    make_hr_agent_task,
    make_llm_judge_scorer,
    make_semantic_similarity_scorer,
):
    golden_dataset = langfuse.get_dataset("ci")

    result = golden_dataset.run_experiment(
        name="ci-eval",
        task=make_hr_agent_task(),
        evaluators=[
            keyword_overlap_scorer,
            make_semantic_similarity_scorer(),
            make_llm_judge_scorer(),
        ],
    )

    scores = defaultdict(list)
    for item in result.item_results:
        for e in item.evaluations:
            scores[e.name].append(e.value)

    failures = [
        f"{name} {sum(values) / len(values):.2f} < {THRESHOLDS[name]}"
        for name, values in scores.items()
        if sum(values) / len(values) < THRESHOLDS[name]
    ]
    assert not failures, f"below threshold: {', '.join(failures)}"
