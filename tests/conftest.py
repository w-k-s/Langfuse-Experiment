import pytest
from dotenv import load_dotenv
from uuid import uuid4
from langfuse import Langfuse, get_client
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from main import build_graph, Deps


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    load_dotenv()


@pytest.fixture(scope="session")
def langfuse() -> Langfuse:
    return get_client()


@pytest.fixture(scope="session")
def llm() -> ChatOllama:
    return ChatOllama(model="llama2:7b", temperature=0)


@pytest.fixture(scope="session")
def graph():
    return build_graph()


@pytest.fixture(scope="session")
def make_hr_agent_task(langfuse, graph, llm):
    def _make():
        def task(*, item, **kwargs):
            result = graph.invoke(
                {"messages": [HumanMessage(item.input)]},
                {"configurable": {"thread_id": str(uuid4())}},
                context=Deps(langfuse, llm),
            )
            return result["messages"][-1].content

        return task

    return _make
