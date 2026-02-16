"""Vector store utility functions for the chatbot."""

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_core.tools import tool


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


def create_hybrid_search_tool(
    db_path: str = "doctors.db",
    vector_store_dir: str = "./chroma_langchain_db",
    name: str = "hybrid_search",
    description: str = "Search for medical skills and specialties using hybrid retrieval",
    k: int = 5
):
    """
    Create a LangChain tool for hybrid search (BM25 + vector).
    
    This function provides a hybrid retrieval tool that combines BM25 lexical search
    with vector semantic search for improved retrieval performance.
    
    Args:
        db_path: Path to database
        vector_store_dir: Vector store directory
        name: Tool name
        description: Tool description
        k: Number of results to return
    
    Returns:
        LangChain tool instance for hybrid search
    """
    from hybrid_retrieval import create_hybrid_search_tool as _create_hybrid_tool
    return _create_hybrid_tool(db_path, vector_store_dir, name, description, k)


def create_sql_vector_search_tool(
    db_path: str = "doctors.db",
    vector_store_dir: str = "./chroma_langchain_db",
    name: str = "sql_vector_search",
    description: str = "Search for doctors using SQL filtering + vector ranking + schedule awareness",
    k: int = 5,
    max_candidates: int = 200,
):
    """
    Create a LangChain tool that uses SQL filtering + vector ranking.

    Args:
        db_path: Path to database
        vector_store_dir: Vector store directory
        name: Tool name
        description: Tool description
        k: Number of results to return
        max_candidates: Max SQL candidates to rank

    Returns:
        LangChain tool instance for SQL + vector search
    """
    from sql_vector_retriever import SQLVectorRetriever

    retriever = SQLVectorRetriever(
        db_path=db_path,
        vector_store_dir=vector_store_dir,
        max_candidates=max_candidates,
    )

    @tool(name)
    def sql_vector_search_tool(query: str) -> str:
        """Search for doctors using SQL + vector + schedule-aware ranking."""
        results = retriever.retrieve(query, k=k)
        if not results:
            return "No matching doctors found."

        lines = []
        for result in results:
            availability = result.get("next_available", {})
            days = availability.get("days_until")
            day_name = availability.get("day_of_week")
            start_hour = availability.get("start_hour")

            if days is None:
                availability_text = "No upcoming availability"
            else:
                time_text = f" at {int(start_hour):02d}:00" if start_hour is not None else ""
                availability_text = f"Available in {days} day(s) on {day_name}{time_text}"

            lines.append(
                f"{result['name']} | {result['specialty']} | {availability_text} | score={result['relevance_score']}"
            )

        return "\n".join(lines)

    sql_vector_search_tool.description = description
    return sql_vector_search_tool


def init_embeddings(model="text-embedding-3-small"):
    """Initialize OpenAI embeddings."""
    return OpenAIEmbeddings(model=model)

