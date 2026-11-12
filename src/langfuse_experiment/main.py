import sys
import time
import argparse
from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langfuse_experiment.app import AppContext
from langfuse_experiment.llm_ops import publish_prompt, publish_dataset
from langfuse_experiment.rag import index_document
from langfuse_experiment.graph import build_graph
from langfuse_experiment.telegram import send, listen


def chat(graph, app: AppContext):
    config = app.runnable_config()
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

        if result.get("__interrupt__"):
            hr_prompt = result["__interrupt__"][0].value
            print(f"[Waiting on HR staff to reply on WhatsApp]: {hr_prompt}")

            state = graph.get_state(config)
            while state.next:
                time.sleep(5)
                state = graph.get_state(config)
            result = state.values

        print("AI: {}".format(result["messages"][-1].text))


def main():
    load_dotenv()
    app = AppContext()
    graph = build_graph(app)

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

    jabber_subparser = subparsers.add_parser("telegram", help="Test Telegram")
    jabber_subparser.add_argument("-s", "--send", help="Message to send")
    jabber_subparser.add_argument(
        "-l", "--listen", action="store_true", help="Run Telegram Listener (blocking)"
    )

    args = parser.parse_args()

    if args.command == "chat":
        chat(graph=graph, app=app)
    elif args.command == "prompts":
        if args.publish:
            publish_prompt(app, args.publish)
    elif args.command == "datasets":
        if args.publish:
            publish_dataset(app, args.publish)
    elif args.command == "rag":
        if args.index:
            index_document(app, args.index)
    elif args.command == "jabber":
        if args.send:
            send(args.send, to=args.to)
        if args.listen:
            listen(app=app, graph=graph)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
