import os
import boto3
import chromadb
import langfuse_experiment.config as config
from langchain_aws import BedrockEmbeddings, ChatBedrockConverse


def build_model():
    return ChatBedrockConverse(
        model_id=config.BEDROCK_TEXT_MODEL_ID,
        region_name=config.BEDROCK_REGION,
        temperature=0,
    )


def build_embeddings():
    return BedrockEmbeddings(
        model_id=config.BEDROCK_EMBEDDING_MODEL_ID,
        region_name=config.BEDROCK_REGION,
    )


def build_chroma():
    return chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
        cloud_host=os.getenv("CHROMA_HOST"),
    )
