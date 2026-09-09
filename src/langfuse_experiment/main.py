import sys
import argparse
from uuid import uuid4
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain.messages import HumanMessage
from langfuse_experiment.app import AppContext
from langfuse_experiment.llm_ops import publish_prompt, publish_dataset
from langfuse_experiment.rag import index_document
from langfuse_experiment.graph import build_graph


def chat(app):
    graph = build_graph(app)

    config: RunnableConfig = {
        "configurable": {
            "thread_id": str(uuid4()),
        },
        "callbacks": [app.callback_handler],
    }

    while True:
        user_input = input("Human: ")

        if user_input.lower() == "q":
            print("Bye")
            break

        result = graph.invoke(
            {"messages": [HumanMessage(user_input)]},
            config,
            context=app,
        )
        print("AI: {}".format(result["messages"][-1].text))


def main():
    load_dotenv()
    app = AppContext()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompts_subparser = subparsers.add_parser("prompts", help="Prompt registry actions")
    prompts_subparser.add_argument("-p", "--publish", help="Publish prompt to registry")

    prompts_subparser = subparsers.add_parser("datasets", help="Dataset Actions")
    prompts_subparser.add_argument(
        "-p", "--publish", help="Publish dataset to registry"
    )

    subparsers.add_parser("chat", help="Chat with agent")

    rag_subparser = subparsers.add_parser("rag", help="RAG Actions")
    rag_subparser.add_argument("-i", "--index", help="Index document")

    args = parser.parse_args()

    if args.command == "chat":
        chat(app)
    elif args.command == "prompts":
        if args.publish:
            publish_prompt(app, args.publish)
    elif args.command == "datasets":
        if args.publish:
            publish_dataset(app, args.publish)
    elif args.command == "rag":
        if args.index:
            index_document(app, args.index)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
