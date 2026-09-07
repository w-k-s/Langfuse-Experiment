import chromadb
from dataclasses import dataclass
from langfuse import Langfuse
from langchain.chat_models import BaseChatModel

BEDROCK_REGION = "ap-south-1"
BEDROCK_TEXT_MODEL_ID = "meta.llama3-70b-instruct-v1:0"
BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
BEDROCK_LLM_JUDGE_MODEL_ID = "openai.gpt-oss-120b-1:0"


@dataclass
class ContextSchema:
    langfuse: Langfuse
    llm: BaseChatModel
    chromadb: chromadb.CloudClient
