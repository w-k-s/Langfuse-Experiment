from langfuse import propagate_attributes
from langfuse_experiment.config import ContextSchema
from langchain.chat_models import BaseChatModel
from langgraph.runtime import Runtime
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.runnables import RunnableConfig


def call_model(
    state: MessagesState, runtime: Runtime[ContextSchema], config: RunnableConfig
):
    langfuse = runtime.context.langfuse
    llm = runtime.context.llm
    thread_id = config["configurable"]["thread_id"]

    with propagate_attributes(session_id=thread_id):

        with langfuse.start_as_current_observation(
            as_type="span", name="call-model"
        ) as root_span:

            prompt_client = langfuse.get_prompt("hr_agent")
            system_prompt = prompt_client.compile()
            messages = [system_prompt] + state["messages"]

            with root_span.start_as_current_observation(
                as_type="generation",
                name="generate-response",
                model=runtime.context.llm.model,
                input=messages,
                prompt=prompt_client,
                model_parameters={"temperature": llm.temperature},
            ) as gen:
                ai_msg = llm.invoke(messages)

                gen.update(output=ai_msg, usage_details=ai_msg.usage_metadata)

                return {"messages": [ai_msg]}


def build_model():
    return ChatOllama(
        model="llama2:7b",
        temperature=0,
    )


def build_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")


def build_graph():
    workflow = StateGraph(MessagesState, context_schema=ContextSchema)
    workflow.add_node(call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)
    return workflow.compile(checkpointer=InMemorySaver())
