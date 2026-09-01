def keyword_overlap_scorer(*, input, output, expected_output, metadata, **kwargs):
    if metadata.get("eval") != "contains":  # not my item — skip
        return []  # returning [] contributes no score
    # ... actual scoring for A ...
    return {"name": "eval_a", "value": score}


def semantic_similarity_scorer(*, input, output, expected_output, metadata, **kwargs):
    if metadata.get("eval") != "similar":
        return []
    # ... actual scoring for B ...
    return {"name": "eval_b", "value": score}


def llm_judge_scorer(*, input, output, expected_output, metadata, **kwargs):
    if metadata.get("eval") != "llm-rubrik":
        return []
    # ... actual scoring for B ...
    return {"name": "eval_b", "value": score}


def test_evals(langfuse, make_hr_agent_task):
    golden_dataset = langfuse.get_dataset("ci")

    golden_dataset.run_experiment(
        name="ci-eval",
        task=make_hr_agent_task(),
        evaluators=[
            keyword_overlap_scorer,
            semantic_similarity_scorer,
            llm_judge_scorer,
        ],
    )
