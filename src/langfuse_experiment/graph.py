from uuid import uuid4
from langchain_core.tools import tool

from langfuse_experiment.app import AppContext
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools.retriever import create_retriever_tool
from langchain.tools import tool, ToolRuntime
from langgraph.types import interrupt
from langfuse_experiment.telegram import send


@dynamic_prompt
def hr_agent_prompt(request: ModelRequest) -> str:
    prompt_client = request.runtime.context.langfuse.get_prompt("hr_agent")
    return prompt_client.compile()


@tool
def ask_hr_manager(question: str, runtime: ToolRuntime):
    """Escalate a question to a human HR manager.
    Use this when the question cannot be answered from the HR policy.
    """

    thread_id = runtime.config["configurable"]["thread_id"]
    print(f"[Sending WhatsApp Message]: {question}")
    send(msg=question, thread=thread_id)

    feedback = interrupt("Please wait while we a member of the HR Staff")

    return feedback


def build_graph(app: AppContext):
    retriever_tool = create_retriever_tool(
        app.retriever,
        name="search_hr_manuals",
        description=(
            "Search the company HR policies and procedures manuals. "
            "Use this for any question about HR policy, leave, benefits, "
            "notice periods, disciplinary procedures, or workplace conduct. "
            "Input should be a focused natural-language query."
        ),
    )

    return create_agent(
        app.llm,
        tools=[retriever_tool, ask_hr_manager],
        middleware=[hr_agent_prompt],
        context_schema=AppContext,
        checkpointer=InMemorySaver(),
    )
