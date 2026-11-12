import os
import litellm
import pytest
from dotenv import load_dotenv

from uuid import uuid4
from langfuse import Evaluation
from langchain.messages import HumanMessage
from ragas.embeddings.base import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
)
import langfuse_experiment.config as config
from langfuse_experiment.graph import (
    build_graph,
    AppContext,
)
from langchain_aws import ChatBedrockConverse


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "env(name): mark test to run only on named environment"
    )


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
def ragas_metrics():

    os.environ["AWS_REGION_NAME"] = config.BEDROCK_REGION
    llm = llm_factory(
        f"bedrock/{config.BEDROCK_LLM_JUDGE_MODEL_ID}",
        provider="litellm",
        client=litellm.completion,
        temperature=0,
    )

    embeddings = embedding_factory(
        "litellm",
        model=f"bedrock/{config.BEDROCK_EMBEDDING_MODEL_ID}",
    )

    return [Faithfulness(llm), AnswerRelevancy(llm, embeddings)]


@pytest.fixture(scope="session")
def ragas_evaluators(ragas_metrics):
    def make_ragas_evaluator(metric):
        async def evaluator(*, input, output, **kwargs):
            if isinstance(metric, Faithfulness):
                result = await metric.ascore(
                    user_input=input,
                    response=output["answer"],
                    retrieved_contexts=output["contexts"],
                )
            else:
                result = await metric.ascore(
                    user_input=input,
                    response=output["answer"],
                )
            return Evaluation(name=metric.name, value=float(result.value))

        return evaluator

    return [make_ragas_evaluator(metric) for metric in ragas_metrics]


@pytest.fixture(scope="session")
def make_rag_task(app, graph):
    def _make():
        def rag_task(*, item, **kwargs):
            question = item.input
            contexts = [d.page_content for d in app.retriever.invoke(question)]

            response = graph.invoke(
                {"messages": [HumanMessage(item.input)]},
                {
                    "configurable": {"thread_id": str(uuid4())},
                },
                context=app,
            )
            # Return the contexts alongside the answer so evaluators can verify against them
            return {
                "answer": response["messages"][-1].text,
                "contexts": contexts,
            }

        return rag_task

    return _make
