#!/usr/bin/env python3
"""Diagnostic: Compare what each retriever returns for sample queries."""

import json
import time
from pathlib import Path

try:
    from retrieval_advanced import AdvancedRetriever
    from hybrid_retrieval import HybridRetriever
    from vector_utils import init_embeddings, init_vector_store
except ImportError:
    from .retrieval_advanced import AdvancedRetriever
    from .hybrid_retrieval import HybridRetriever
    from .vector_utils import init_embeddings, init_vector_store


def show_retriever_comparison():
    """Show what each retriever returns for sample queries."""
    
    # Load aligned dataset
    dataset_path = Path(__file__).parent / "evaluation_dataset_aligned.json"
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    # Select 3 sample queries (easy, medium, hard)
    easy_q = next(q for q in dataset['queries'] if q.get('difficulty') == 'easy')
    medium_q = next(q for q in dataset['queries'] if q.get('difficulty') == 'medium')
    hard_q = next(q for q in dataset['queries'] if q.get('difficulty') == 'hard')
    
    sample_queries = [
        (easy_q, "EASY"),
        (medium_q, "MEDIUM"),
        (hard_q, "HARD")
    ]
    
    # Initialize retrievers
    print("Initializing retrievers...")
    
    embeddings = init_embeddings()
    vector_store = init_vector_store(
        name="medical_collection",
        embeddings=embeddings,
        directory="./chroma_langchain_db"
    )
    
    advanced = AdvancedRetriever()
    hybrid = HybridRetriever(use_vector_store=True)
    
    print("[OK] Retrievers initialized\n")
    
    for query_obj, label in sample_queries:
        query = query_obj['query']
        expected = query_obj.get('relevance_grades', {})
        relevant_docs = set(doc for doc, grade in expected.items() if grade >= 2)
        
        print("="*70)
        print(f"{label}: {query}")
        print(f"Expected relevant docs: {relevant_docs}")
        print()
        
        # Vector retriever
        print("[Vector Only]")
        start = time.time()
        vec_results = vector_store.similarity_search(query, k=10)
        vec_time = (time.time() - start) * 1000
        vec_docs = [doc.page_content for doc in vec_results]
        vec_found = set(vec_docs) & relevant_docs
        print(f"  Results ({vec_time:.1f}ms): {vec_docs[:5]}...")
        print(f"  Found {len(vec_found)}/{len(relevant_docs)} expected: {vec_found}")
        print()
        
        # Hybrid retriever
        print("[Hybrid (BM25+Vector)]")
        start = time.time()
        hybrid_results = hybrid.hybrid_search(query, k=10)
        hybrid_time = (time.time() - start) * 1000
        hybrid_docs = [doc for doc, _ in hybrid_results]
        hybrid_found = set(hybrid_docs) & relevant_docs
        print(f"  Results ({hybrid_time:.1f}ms): {hybrid_docs[:5]}...")
        print(f"  Found {len(hybrid_found)}/{len(relevant_docs)} expected: {hybrid_found}")
        print()
        
        # Advanced retriever
        print("[Advanced (Multi-Stage)]")
        start = time.time()
        adv_results = advanced.retrieve_with_skill_boost(query, k=10)
        adv_time = (time.time() - start) * 1000
        adv_docs = [doc for doc, _ in adv_results]
        adv_found = set(adv_docs) & relevant_docs
        print(f"  Results ({adv_time:.1f}ms): {adv_docs[:5]}...")
        print(f"  Found {len(adv_found)}/{len(relevant_docs)} expected: {adv_found}")
        print()


if __name__ == "__main__":
    show_retriever_comparison()
