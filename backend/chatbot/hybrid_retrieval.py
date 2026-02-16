"""
Hybrid retrieval system combining BM25 and vector-based semantic search.
"""

import numpy as np
from typing import List, Tuple, Optional
from rank_bm25 import BM25Okapi

try:
    from database_utils import init_database, safe_query_as_list
    from vector_utils import init_embeddings, init_vector_store
except ImportError:
    from .database_utils import init_database, safe_query_as_list
    from .vector_utils import init_embeddings, init_vector_store


class HybridRetriever:
    """Hybrid retrieval combining BM25 (lexical) and vector (semantic) search."""
    
    def __init__(
        self,
        db_path: str = "doctors.db",
        vector_store_dir: str = "./chroma_langchain_db",
        embedding_model: str = "text-embedding-3-small",
        bm25_k: int = 50,
        final_k: int = 10,
        use_vector_store: bool = True
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            db_path: Path to SQLite database
            vector_store_dir: Directory for vector store
            embedding_model: Embedding model name
            bm25_k: Number of candidates to retrieve from BM25
            final_k: Final number of results after reranking
            use_vector_store: Whether to use vector store (requires API key)
        """
        self.db_path = db_path
        self.vector_store_dir = vector_store_dir
        self.embedding_model = embedding_model
        self.bm25_k = bm25_k
        self.final_k = final_k
        self.use_vector_store = use_vector_store
        
        # Initialize components
        self._setup_database()
        self._setup_bm25()
        if use_vector_store:
            try:
                self._setup_vector_store()
            except Exception as e:
                print(f"⚠️  Vector store initialization failed: {e}")
                print("   Continuing with BM25 only mode")
                self.use_vector_store = False
    
    def _setup_database(self):
        """Initialize database connection."""
        self.db = init_database(self.db_path)
    
    def _setup_bm25(self):
        """Initialize BM25 index with skills and specialties."""
        # Get all skills and specialties
        skills = safe_query_as_list(self.db, "skills", "skill")
        specialties = safe_query_as_list(self.db, "doctors", "specialty")
        
        # Combine and deduplicate
        self.corpus = list(set(skills + specialties))
        
        # Tokenize corpus (simple whitespace tokenization)
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        
        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        print(f"✅ BM25 index created with {len(self.corpus)} documents")
    
    def _setup_vector_store(self):
        """Initialize vector store."""
        embeddings = init_embeddings(self.embedding_model)
        self.vector_store = init_vector_store(
            name="medical_collection",
            embeddings=embeddings,
            directory=self.vector_store_dir
        )
        print(f"✅ Vector store loaded")
    
    def search_bm25(self, query: str, k: int = None) -> List[Tuple[str, float]]:
        """
        Perform BM25 search.
        
        Args:
            query: Search query
            k: Number of results (default: self.bm25_k)
        
        Returns:
            List of (document, score) tuples
        """
        k = k or self.bm25_k
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_k_indices = np.argsort(scores)[::-1][:k]
        
        # Return documents with scores
        results = [(self.corpus[i], scores[i]) for i in top_k_indices if scores[i] > 0]
        
        return results
    
    def search_vector(self, query: str, k: int = None) -> List[Tuple[str, float]]:
        """
        Perform vector similarity search.
        
        Args:
            query: Search query
            k: Number of results (default: self.final_k)
        
        Returns:
            List of (document, score) tuples
        """
        if not self.use_vector_store:
            return []
        
        k = k or self.final_k
        
        # Use similarity_search_with_score for relevance scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Convert to (document, score) tuples
        # Note: ChromaDB returns distance, we convert to similarity (1 - distance)
        return [(doc.page_content, 1.0 - score) for doc, score in results]
    
    def rerank_with_vector(
        self,
        query: str,
        bm25_candidates: List[Tuple[str, float]],
        k: int = None
    ) -> List[Tuple[str, float]]:
        """
        Rerank BM25 candidates using vector similarity.
        
        Args:
            query: Original search query
            bm25_candidates: BM25 retrieved documents with scores
            k: Number of final results (default: self.final_k)
        
        Returns:
            Reranked list of (document, combined_score) tuples
        """
        k = k or self.final_k
        
        if not bm25_candidates:
            return []
        
        # Get candidate documents
        candidate_docs = [doc for doc, _ in bm25_candidates]
        
        # Get vector scores for all candidates
        # We'll search with higher k to cover all candidates
        vector_results = self.vector_store.similarity_search_with_score(
            query, 
            k=min(len(candidate_docs) * 2, 100)
        )
        
        # Create document to vector score mapping
        vector_scores = {
            doc.page_content: 1.0 - score 
            for doc, score in vector_results
        }
        
        # Combine scores (weighted average)
        # BM25: 40%, Vector: 60%
        combined_results = []
        for doc, bm25_score in bm25_candidates:
            vector_score = vector_scores.get(doc, 0.0)
            # Normalize BM25 score (simple min-max if needed)
            bm25_norm = bm25_score / (max([s for _, s in bm25_candidates]) + 1e-10)
            combined_score = 0.4 * bm25_norm + 0.6 * vector_score
            combined_results.append((doc, combined_score))
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x[1], reverse=True)
        
        return combined_results[:k]
    
    def hybrid_search(self, query: str, k: int = None) -> List[Tuple[str, float]]:
        """
        Perform hybrid search: BM25 retrieval + vector reranking.
        
        Args:
            query: Search query
            k: Number of final results (default: self.final_k)
        
        Returns:
            List of (document, score) tuples
        """
        k = k or self.final_k
        
        # Stage 1: BM25 retrieval
        bm25_results = self.search_bm25(query, k=self.bm25_k)
        
        if not bm25_results:
            # Fallback to pure vector search if available
            if self.use_vector_store:
                return self.search_vector(query, k=k)
            return []
        
        # Stage 2: Vector reranking (if available)
        if self.use_vector_store:
            final_results = self.rerank_with_vector(query, bm25_results, k=k)
        else:
            # Return BM25 results only
            final_results = bm25_results[:k]
        
        return final_results


def create_hybrid_search_tool(
    db_path: str = "doctors.db",
    vector_store_dir: str = "./chroma_langchain_db",
    name: str = "hybrid_search",
    description: str = "Search for medical skills and specialties using hybrid retrieval",
    k: int = 5
):
    """
    Create a LangChain tool for hybrid search.
    
    Args:
        db_path: Path to database
        vector_store_dir: Vector store directory
        name: Tool name
        description: Tool description
        k: Number of results to return
    
    Returns:
        LangChain tool instance
    """
    from langchain.tools import Tool
    
    # Initialize retriever
    retriever = HybridRetriever(
        db_path=db_path,
        vector_store_dir=vector_store_dir,
        bm25_k=50,
        final_k=k
    )
    
    def search_func(query: str) -> str:
        """Search function for the tool."""
        results = retriever.hybrid_search(query, k=k)
        if not results:
            return "No relevant results found."
        
        # Format results
        formatted = "\n".join([
            f"{i+1}. {doc} (relevance: {score:.3f})"
            for i, (doc, score) in enumerate(results)
        ])
        return formatted
    
    return Tool(
        name=name,
        description=description,
        func=search_func
    )


# Testing
if __name__ == "__main__":
    import os
    
    print("Initializing Hybrid Retriever...")
    # Check if API key is available
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    retriever = HybridRetriever(use_vector_store=has_api_key)
    
    # Test queries
    test_queries = [
        "cardiology",
        "heart surgery",
        "angioplasty skills",
        "pediatric care",
        "brain surgery"
    ]
    
    print("\n" + "="*60)
    print("HYBRID RETRIEVAL COMPARISON")
    print("="*60)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        
        # BM25 only
        bm25_results = retriever.search_bm25(query, k=5)
        print("\n📊 BM25 Results (Top 5):")
        for i, (doc, score) in enumerate(bm25_results[:5], 1):
            print(f"  {i}. {doc} (score: {score:.3f})")
        
        if retriever.use_vector_store:
            # Vector only
            vector_results = retriever.search_vector(query, k=5)
            print("\n🧠 Vector Results (Top 5):")
            for i, (doc, score) in enumerate(vector_results[:5], 1):
                print(f"  {i}. {doc} (score: {score:.3f})")
        
        # Hybrid
        hybrid_results = retriever.hybrid_search(query, k=5)
        print(f"\n🔀 {'Hybrid' if retriever.use_vector_store else 'BM25-only'} Results (Top 5):")
        for i, (doc, score) in enumerate(hybrid_results[:5], 1):
            print(f"  {i}. {doc} (score: {score:.3f})")
