"""Vector store utility functions for the chatbot."""

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents.agent_toolkits import create_retriever_tool


def init_vector_store(name, embeddings, directory):
    """Initialize a vector store with the given name, embeddings, and directory."""
    return Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory=directory,
    )


def add_texts_to_vector_store(vector_store, texts):
    """Add texts to the vector store."""
    if not texts:
        return
    vector_store.add_texts(texts)


def get_retriever(vector_store, k=5):
    """Create a retriever from the vector store."""
    return vector_store.as_retriever(search_kwargs={"k": k})


def create_search_tool(vector_store, name, description, k=5):
    """Create a retriever tool for searching proper nouns."""
    retriever = get_retriever(vector_store, k=k)
    return create_retriever_tool(
        retriever,
        name=name,
        description=description,
    )


def init_embeddings(model="text-embedding-3-small"):
    """Initialize OpenAI embeddings."""
    return OpenAIEmbeddings(model=model)
