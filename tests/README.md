# Legacy custom scorers

`keyword_overlap_scorer`, `semantic_similarity_scorer` and `llm_judge_scorer` (in
[conftest.py](conftest.py)) are no longer used. Evaluation is done with ragas instead.
They are kept for future reference.

## How they were used

### 1. The dataset

Each Langfuse dataset item carried a `metadata.eval` key with a value naming the score function that scored it: one of [`contains`, `similar`, `llm-rubrik`.

```yaml
name: ci
description: "CI Dataset"
items:
  - input: Can I get a raise?
    expected_output: "No"
    metadata:
      eval: contains
  - input: I'd like to report a case of physical violence.
    expected_output: "Incident is dismissed."
    metadata:
      eval: llm-rubrik
```

### 2. The scorers

Each scorer first checked if it was the evaluator for the current dataset item. If not, it returned an empty array (in langfuse, this is the equivalent of returning no score).

```python
import re
from math import sqrt
from uuid import uuid4

import pytest
from langchain.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from langfuse_experiment.graph import AppContext

class JudgeResult(BaseModel):
    score: float  # 0-1
    reasoning: str

@pytest.fixture(scope="session")
def judge_chain(judge_llm):
    judge_prompt = ChatPromptTemplate.from_template(
        "You are grading an HR assistant's answer against a reference answer.\n"
        "Question: {input}\n"
        "Reference answer: {expected_output}\n"
        "Assistant's answer: {output}\n"
        "Give a correctness score from 0 (wrong) to 1 (matches the reference), "
        "and a one-sentence reason. "
        "Important: You must only compare answer. No other criteria should influence your scoring."
    )

    return judge_prompt | judge_llm.with_structured_output(JudgeResult)

@pytest.fixture(scope="session")
def make_llm_judge_scorer(judge_chain):
    def _make():
        def llm_judge_scorer(*, input, output, expected_output, metadata, **kwargs):
            if metadata.get("eval") != "llm-rubrik":
                return []

            result = judge_chain.invoke(
                {
                    "input": input,
                    "output": output,
                    "expected_output": expected_output,
                }
            )
            return {
                "name": metadata.get("eval"),
                "value": result.score,
                "comment": result.reasoning,
            }

        return llm_judge_scorer

    return _make


@pytest.fixture(scope="session")
def make_semantic_similarity_scorer(app: AppContext):
    def _make():
        def semantic_similarity_scorer(
            *, input, output, expected_output, metadata, **kwargs
        ):
            if metadata.get("eval") != "similar":
                return []

            actual, expected = app.embeddings.embed_documents([output, expected_output])
            dot = sum(a * b for a, b in zip(actual, expected))
            norm = sqrt(sum(a * a for a in actual)) * sqrt(sum(b * b for b in expected))
            similarity = dot / norm if norm else 0.0

            return {
                "name": metadata.get("eval"),
                "value": max(0.0, min(1.0, similarity)),
            }

        return semantic_similarity_scorer

    return _make


PATTERN = r"\w+"

@pytest.fixture(scope="session")
def make_keyword_overlap_scorer(app: AppContext):
    def _make():
        def keyword_overlap_scorer(
            *, input, output, expected_output, metadata, **kwargs
        ):
            if metadata.get("eval") != "contains":
                return []

            output_keywords = set(re.findall(PATTERN, output.lower()))
            expected_keywords = set(re.findall(PATTERN, expected_output.lower()))
            overlap = len(expected_keywords & output_keywords) / len(expected_keywords)
            return {"name": metadata.get("eval"), "value": overlap}

        return keyword_overlap_scorer

    return _make


@pytest.fixture(scope="session")
def make_hr_agent_task(app: AppContext, graph):
    def _make():
        def task(*, item, **kwargs):
            result = graph.invoke(
                {"messages": [HumanMessage(item.input)]},
                {
                    "configurable": {"thread_id": str(uuid4())},
                    "callbacks": [app.callback_handler],
                },
                context=app,
            )
            return result["messages"][-1].text

        return task

    return _make
```


### 3. Overall scoring

Langfuse's `run_experiment` ran the graph over the dataset with all three scorers attached;
results were grouped by score name, averaged, and each average compared against a
per-eval threshold. One assert covered the whole suite:

```python
from collections import defaultdict

THRESHOLDS = {"contains": 1.0, "similar": 0.2, "llm-rubrik": 0.2}

def test_evals(
    app,
    make_hr_agent_task,
    make_llm_judge_scorer,
    make_semantic_similarity_scorer,
    make_keyword_overlap_scorer,
):
    rag_dataset = app.langfuse.get_dataset("rag_dataset")

    result = rag_dataset.run_experiment(
        name="rag-eval",
        task=make_hr_agent_task(),
        evaluators=[
            make_keyword_overlap_scorer(),
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
```
