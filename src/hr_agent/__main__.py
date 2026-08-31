from dataclasses import dataclass
import sys
import argparse
from dotenv import load_dotenv
from langchain.chat_models import BaseChatModel
from langfuse import Langfuse, get_client
from langchain_ollama import ChatOllama
from langgraph.runtime import Runtime
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from langchain.messages import HumanMessage, SystemMessage
from src.hr_agent.llm_ops import publish_prompt, publish_dataset


@dataclass
class Deps:
    prompt_registry: Langfuse
    llm: BaseChatModel


def call_model(state: MessagesState, runtime: Runtime[Deps]):
    prompt_client = runtime.context.prompt_registry.get_prompt("hr_agent")
    system_prompt = prompt_client.compile()
    ai_msg = runtime.context.llm.invoke([system_prompt] + state["messages"])
    return {"messages": [ai_msg]}


def chat(langfuse):
    llm = ChatOllama(
        model="llama2:7b",
        temperature=0,
    )

    workflow = StateGraph(MessagesState, context_schema=Deps)
    workflow.add_node(call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)

    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("Human: ")

        if user_input.lower() == "q":
            print("Bye")
            break

        result = graph.invoke(
            {"messages": [HumanMessage(user_input)]},
            config,
            context=Deps(langfuse, llm),
        )
        print("AI: {}".format(result["messages"][-1].content))


if __name__ == "__main__":
    load_dotenv()
    langfuse = get_client()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompts_subparser = subparsers.add_parser("prompts", help="Prompt registry actions")
    prompts_subparser.add_argument("-p", "--publish", help="Publish prompt to registry")

    prompts_subparser = subparsers.add_parser("datasets", help="Dataset Actions")
    prompts_subparser.add_argument(
        "-p", "--publish", help="Publish dataset to registry"
    )

    chat_subparser = subparsers.add_parser("chat", help="Chat with agent")

    args = parser.parse_args()

    if args.command == "chat":
        chat(langfuse)
    elif args.command == "prompts":
        if args.publish:
            publish_prompt(langfuse, args.publish)
    elif args.command == "datasets":
        if args.publish:
            publish_dataset(langfuse, args.publish)
    else:
        parser.print_help()
        sys.exit(1)
