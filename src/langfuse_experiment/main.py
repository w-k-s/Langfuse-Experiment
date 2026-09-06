import os
import sys
import argparse
import chromadb
from uuid import uuid4
from dotenv import load_dotenv
from langfuse import get_client
from langchain_core.runnables import RunnableConfig
from langchain.messages import HumanMessage
from langfuse_experiment.llm_ops import publish_prompt, publish_dataset
from langfuse_experiment.rag import index_document
from langfuse_experiment.graph import (
    build_graph,
    build_model,
    build_embeddings,
    ContextSchema,
)


def chat(langfuse, chroma):
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
            context=ContextSchema(langfuse, llm, chroma),
        )
        print("AI: {}".format(result["messages"][-1].content))


def main():
    load_dotenv()
    langfuse = get_client()
    chroma = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
        cloud_host=os.getenv("CHROMA_HOST"),
    )
    embeddings = build_embeddings()

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
        chat(langfuse)
    elif args.command == "prompts":
        if args.publish:
            publish_prompt(langfuse, args.publish)
    elif args.command == "datasets":
        if args.publish:
            publish_dataset(langfuse, args.publish)
    elif args.command == "rag":
        if args.index:
            index_document(chroma, embeddings, args.index)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
