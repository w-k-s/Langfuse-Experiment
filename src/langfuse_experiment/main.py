import sys
import argparse
from uuid import uuid4
from dotenv import load_dotenv
from langfuse import get_client
from langchain_core.runnables import RunnableConfig
from langchain.messages import HumanMessage
from langfuse_experiment.llm_ops import publish_prompt, publish_dataset
from langfuse_experiment.graph import build_graph, build_model, ContextSchema


def chat(langfuse):
    llm = build_model()

    graph = build_graph()

    config: RunnableConfig = {"configurable": {"thread_id": str(uuid4())}}

    while True:
        user_input = input("Human: ")

        if user_input.lower() == "q":
            print("Bye")
            break

        result = graph.invoke(
            {"messages": [HumanMessage(user_input)]},
            config,
            context=ContextSchema(langfuse, llm),
        )
        print("AI: {}".format(result["messages"][-1].content))


def main():
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

    subparsers.add_parser("chat", help="Chat with agent")

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


if __name__ == "__main__":
    main()
