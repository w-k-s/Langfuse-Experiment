import pytest
from dotenv import load_dotenv
from math import sqrt
from uuid import uuid4
from langchain.messages import HumanMessage
import langfuse_experiment.config as config
from langfuse_experiment.graph import (
    build_graph,
    AppContext,
)
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class JudgeResult(BaseModel):
    score: float  # 0-1
    reasoning: str


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    load_dotenv()


@pytest.fixture(scope="session")
def app() -> AppContext:
    return AppContext()


@pytest.fixture(scope="session")
def graph(app: AppContext):
    return build_graph(app)


@pytest.fixture(scope="session")
def judge_llm():
    return ChatBedrockConverse(
        model_id=config.BEDROCK_LLM_JUDGE_MODEL_ID,
        region_name=config.BEDROCK_REGION,
        temperature=0,
        reasoning_effort="low",
    )


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
