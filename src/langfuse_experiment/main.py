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
from langfuse_experiment.db import create_tables, create_interrupt


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
            pending = result["__interrupt__"][0]
            question = pending.value
            print(f"[Sending question to HR on Telegram]: {question}")

            chat_id, message_id = send(msg=question)
            create_interrupt(
                chat_id=chat_id,
                message_id=message_id,
                thread_id=config["configurable"]["thread_id"],
                agent_question=question,
                interrupt_id=pending.id,
            )

            state = graph.get_state(config)
            while state.next:
                time.sleep(5)
                state = graph.get_state(config)
            result = state.values

        print("AI: {}".format(result["messages"][-1].text))


def main():
    load_dotenv()
    create_tables()
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

    messaging_subparser = subparsers.add_parser("telegram", help="Test Telegram")
    messaging_subparser.add_argument("-s", "--send", help="Message to send")
    messaging_subparser.add_argument(
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
    elif args.command == "telegram":
        if args.send:
            send(args.send)
        if args.listen:
            listen(app=app, graph=graph)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
