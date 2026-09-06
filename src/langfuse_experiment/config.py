import chromadb
from dataclasses import dataclass
from langfuse import Langfuse
from langchain.chat_models import BaseChatModel


@dataclass
class ContextSchema:
    langfuse: Langfuse
    llm: BaseChatModel
    chromadb: chromadb.CloudClient
