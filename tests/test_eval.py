from collections import defaultdict

THRESHOLDS = {
    "faithfulness": 0.6,
    "answer_relevancy": 0.6,
}


def test_evals(
    app,
    make_rag_task,
    ragas_evaluators,
):
    rag_dataset = app.langfuse.get_dataset("rag_dataset")

    result = rag_dataset.run_experiment(
        name="ci-eval",
        task=make_rag_task(),
        evaluators=ragas_evaluators,
    )

    print(result.format())
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
