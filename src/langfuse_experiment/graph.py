from langfuse_experiment.app import AppContext
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools.retriever import create_retriever_tool


@dynamic_prompt
def hr_agent_prompt(request: ModelRequest) -> str:
    prompt_client = request.runtime.context.langfuse.get_prompt("hr_agent")
    return prompt_client.compile()


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
        tools=[retriever_tool],
        middleware=[hr_agent_prompt],
        context_schema=AppContext,
        checkpointer=InMemorySaver(),
    )
