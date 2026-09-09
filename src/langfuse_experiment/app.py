import os
import chromadb
from typing import Any
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
from langchain_chroma import Chroma
from langchain.chat_models import BaseChatModel
from langchain_aws import BedrockEmbeddings, ChatBedrockConverse
from langchain_core.vectorstores import VectorStoreRetriever
import langfuse_experiment.config as config


class AppContext:
    langfuse: Langfuse
    callback_handler: CallbackHandler
    llm: BaseChatModel
    chroma: Chroma
    embeddings: BedrockEmbeddings
    retriever: VectorStoreRetriever

    def __init__(self):
        self.langfuse = get_client()
        # Initialize Langfuse CallbackHandler for Langchain (tracing)
        self.callback_handler = CallbackHandler()
        self.llm = _build_model()
        self.embeddings = _build_embeddings()
        self.chroma = _build_chroma(self.embeddings)
        self.retriever = self.chroma.as_retriever(
            search_kwargs={"k": config.RETRIEVER_K}
        )


def _build_model():
    return ChatBedrockConverse(
        model_id=config.BEDROCK_TEXT_MODEL_ID,
        region_name=config.BEDROCK_REGION,
        temperature=0,
    )


def _build_embeddings():
    return BedrockEmbeddings(
        model_id=config.BEDROCK_EMBEDDING_MODEL_ID,
        region_name=config.BEDROCK_REGION,
    )


def _build_chroma(embeddings):
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
        cloud_host=os.getenv("CHROMA_HOST"),
    )

    return Chroma(
        client=client,
        collection_name=config.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
