from langfuse import Evaluation
import pytest
from dotenv import load_dotenv

from uuid import uuid4
from langchain.messages import HumanMessage
from ragas import RunConfig, SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    Faithfulness,
    MetricWithEmbeddings,
    MetricWithLLM,
    ResponseRelevancy,
)
import langfuse_experiment.config as config
from langfuse_experiment.graph import (
    build_graph,
    AppContext,
)
from langchain_aws import ChatBedrockConverse


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
def ragas_metrics(judge_llm, app):
    metrics = [Faithfulness(), ResponseRelevancy()]
    llm = LangchainLLMWrapper(judge_llm)
    embeddings = LangchainEmbeddingsWrapper(app.embeddings)

    for metric in metrics:
        if isinstance(metric, MetricWithLLM):
            metric.llm = llm
        if isinstance(metric, MetricWithEmbeddings):
            metric.embeddings = embeddings
        metric.init(RunConfig())
    return metrics


@pytest.fixture(scope="session")
def ragas_evaluators(ragas_metrics):
    def make_ragas_evaluator(metric):
        async def evaluator(*, input, output, **kwargs):
            sample = SingleTurnSample(
                user_input=input,
                retrieved_contexts=output["contexts"],
                response=output["answer"],
            )
            score = await metric.single_turn_ascore(sample)
            return Evaluation(name=metric.name, value=float(score))

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
