import pytest
import asyncio
import json
from collections import defaultdict

from langchain_core.messages import AIMessage
from ragas import SingleTurnSample

THRESHOLDS = {
    "faithfulness": 0.6,
    "answer_relevancy": 0.6,
}


@pytest.mark.offline
def test_offline_evals(
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


@pytest.mark.online
def test_online_eval(app, ragas_metrics):
    live_traces = app.langfuse.api.observations.get_many(
        is_root_observation=True, type="CHAIN", fields="core,io", limit=5
    ).data

    async def score_traces():
        for trace in live_traces:
            question = json.loads(trace.input)["messages"][-1]["content"]
            last_message = json.loads(trace.output)["messages"][-1]
            answer = AIMessage(content=last_message["content"]).text

            retrievals = app.langfuse.api.observations.get_many(
                trace_id=trace.trace_id, type="RETRIEVER", fields="core,io"
            ).data
            contexts = []
            for retrieval in retrievals:
                for doc in json.loads(retrieval.output):
                    contexts.append(doc["page_content"])

            if not contexts:
                continue

            print(
                json.dumps(
                    {
                        "question": question,
                        "answer": answer,
                        "retrieved_contexts": contexts,
                        "trace_id": trace.trace_id,
                    },
                    indent=2,
                ),
            )

            sample = SingleTurnSample(
                user_input=question,
                retrieved_contexts=contexts,
                response=answer,
            )
            for metric in ragas_metrics:
                score = await metric.single_turn_ascore(sample)
                app.langfuse.create_score(
                    name=metric.name, value=float(score), trace_id=trace.trace_id
                )

    asyncio.run(score_traces())
    app.langfuse.flush()
