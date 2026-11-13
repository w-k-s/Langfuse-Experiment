from uuid import uuid4
from langchain_core.tools import tool

from langfuse_experiment.app import AppContext
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_core.tools.retriever import create_retriever_tool
from langchain.tools import tool
from langgraph.types import interrupt
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langfuse_experiment.db import DB_PATH


@dynamic_prompt
def hr_agent_prompt(request: ModelRequest) -> str:
    prompt_client = request.runtime.context.langfuse.get_prompt("hr_agent")
    return prompt_client.compile()


@tool
def ask_hr_manager(question: str):
    """Escalate a question to a human HR manager and wait for their reply.
    Use this when the question cannot be answered from the HR policy.
    Returns the HR manager's answer, which you must relay to the employee.
    """

    hr_answer = interrupt(question)

    return f"The HR manager has answered the employee's question. Their answer: {hr_answer}"


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
        checkpointer=SqliteSaver(
            sqlite3.connect(DB_PATH, check_same_thread=False)
        ),
    )
