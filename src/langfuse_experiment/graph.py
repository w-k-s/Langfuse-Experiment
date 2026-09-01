from dataclasses import dataclass
from langfuse import Langfuse
from langchain.chat_models import BaseChatModel
from langgraph.runtime import Runtime
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama


@dataclass
class ContextSchema:
    prompt_registry: Langfuse
    llm: BaseChatModel


def call_model(state: MessagesState, runtime: Runtime[ContextSchema]):
    prompt_client = runtime.context.prompt_registry.get_prompt("hr_agent")
    system_prompt = prompt_client.compile()
    ai_msg = runtime.context.llm.invoke([system_prompt] + state["messages"])
    return {"messages": [ai_msg]}


def build_model():
    return ChatOllama(
        model="llama2:7b",
        temperature=0,
    )


def build_graph():
    workflow = StateGraph(MessagesState, context_schema=ContextSchema)
    workflow.add_node(call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)
    return workflow.compile(checkpointer=InMemorySaver())
