"""Advanced retriever with multi-stage architecture: expansion → retrieval → reranking."""

from typing import List, Tuple, Dict, Set, Optional
import numpy as np
from collections import defaultdict
import time

try:
    from query_expansion import MedicalQueryExpander
    from hybrid_retrieval import HybridRetriever
    from database_utils import init_database, safe_query_as_list
except ImportError:
    from .query_expansion import MedicalQueryExpander
    from .hybrid_retrieval import HybridRetriever
    from .database_utils import init_database, safe_query_as_list


class AdvancedRetriever:
    """
    Multi-stage advanced retriever:
    1. Query Expansion - Expand with synonyms, abbreviations, procedures
    2. Multi-Query Retrieval - Search with BM25 + Vector on all expansions
    3. Candidate Deduplication - Combine results and score
    4. Optional Reranking - Rank by combined semantic + lexical score
    """
    
    def __init__(
        self,
        db_path: str = "doctors.db",
        vector_store_dir: str = "./chroma_langchain_db",
        use_vector_store: bool = True,
        verbose: bool = False
    ):
        """
        Initialize advanced retriever.
        
        Args:
            db_path: Path to SQLite database
            vector_store_dir: Vector store directory
            use_vector_store: Whether to use vector embeddings
            verbose: Print debug info
        """
        self.db_path = db_path
        self.verbose = verbose
        self.expander = MedicalQueryExpander()
        self.hybrid = HybridRetriever(
            db_path=db_path,
            vector_store_dir=vector_store_dir,
            use_vector_store=use_vector_store
        )
        self.db = init_database(db_path)
        
        # Statistics tracking
        self.expansion_stats = defaultdict(int)
        self.retrieval_stats = defaultdict(int)
    
    def _log(self, msg: str):
        """Print debug message if verbose."""
        if self.verbose:
            print(f"[DEBUG] {msg}")
    
    def retrieve_advanced(
        self,
        query: str,
        k: int = 10,
        top_expansions: int = 5
    ) -> List[Tuple[str, Dict]]:
        """
        Advanced retrieval with expansion and multi-stage ranking.
        
        Args:
            query: Original search query
            k: Number of final results to return
            top_expansions: Number of query expansions to use
        
        Returns:
            List of (document, metadata) tuples with scores
        """
        self._log(f"Query: {query}")
        
        # Stage 1: Query Expansion
        start_time = time.time()
        expansions = self.expander.expand_query(query)
        expansions = expansions[:top_expansions]  # Limit to avoid too many searches
        expansion_time = time.time() - start_time
        self._log(f"Expansions ({len(expansions)}): {expansions[:3]}...")
        self.expansion_stats["total_queries"] += 1
        self.expansion_stats["avg_expansions"] = np.mean([
            self.expansion_stats.get("avg_expansions", 0),
            len(expansions)
        ])
        
        # Stage 2: Multi-Query Retrieval
        start_time = time.time()
        candidate_scores = defaultdict(lambda: {
            "bm25_scores": [],
            "vector_scores": [],
            "sources": [],
            "match_count": 0
        })
        
        for expansion in expansions:
            try:
                # Hybrid search on each expansion
                results = self.hybrid.hybrid_search(expansion, k=50)
                
                for doc, score in results:
                    candidate_scores[doc]["bm25_scores"].append(score)
                    candidate_scores[doc]["sources"].append(expansion)
                    candidate_scores[doc]["match_count"] += 1
                    
            except Exception as e:
                self._log(f"Error retrieving expansion '{expansion}': {e}")
        
        retrieval_time = time.time() - start_time
        self._log(f"Retrieved {len(candidate_scores)} unique candidates in {retrieval_time:.3f}s")
        
        # Stage 3: Candidate Aggregation & Scoring
        start_time = time.time()
        scored_candidates = []
        
        for doc, meta in candidate_scores.items():
            # Combine BM25 scores (multiple expansions might retrieve same doc)
            avg_bm25 = np.mean(meta["bm25_scores"]) if meta["bm25_scores"] else 0.0
            
            # Boost score if matched in multiple expansions (indicates strong relevance)
            multiplicity_boost = min(meta["match_count"] / len(expansions), 1.0)  # 0-1
            
            # Combined score: BM25 + multiplicity boost
            combined_score = (0.7 * avg_bm25) + (0.3 * multiplicity_boost)
            
            scored_candidates.append({
                "doc": doc,
                "score": combined_score,
                "bm25": avg_bm25,
                "multiplicity": multiplicity_boost,
                "match_count": meta["match_count"],
                "expansions": meta["sources"]
            })
        
        # Stage 4: Sort and rerank
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply semantic filtering - optionally filter low-confidence results
        final_results = []
        min_confidence_threshold = 0.3
        
        for candidate in scored_candidates[:k*2]:  # Look at twice k for threshold filtering
            if candidate["score"] >= min_confidence_threshold or len(final_results) < k:
                final_results.append(candidate)
            if len(final_results) >= k:
                break
        
        aggregation_time = time.time() - start_time
        self._log(f"Aggregated {len(final_results)} results in {aggregation_time:.3f}s")
        
        # Convert to return format
        return_results = [
            (
                r["doc"],
                {
                    "score": r["score"],
                    "confidence": r["score"],
                    "matched_expansions": len(set(r["expansions"])),
                    "match_count": r["match_count"],
                    "bm25_score": r["bm25"],
                    "multiplicity_boost": r["multiplicity"]
                }
            )
            for r in final_results[:k]
        ]
        
        return return_results
    
    def retrieve_with_skill_boost(
        self,
        query: str,
        k: int = 10,
        top_expansions: int = 5
    ) -> List[Tuple[str, Dict]]:
        """
        Retrieval with skill-based boosting for procedure queries.
        
        Args:
            query: Search query
            k: Number of results
            top_expansions: Number of expansions to use
        
        Returns:
            List of (document, metadata) tuples
        """
        # Detect skills in query
        detected_skills = self.expander.get_skills_from_query(query)
        detected_specialties = self.expander.get_specialty_from_query(query)
        
        self._log(f"Detected skills: {detected_skills}")
        self._log(f"Detected specialties: {detected_specialties}")
        
        # Get base results
        results = self.retrieve_advanced(query, k=k*2, top_expansions=top_expansions)
        
        # Boost if matching skills or specialties
        boosted = []
        for doc, meta in results:
            boost = 1.0
            
            # Check if doc is a specialty
            if any(spec.lower() in doc.lower() for spec in detected_specialties):
                boost *= 1.5
            
            # Check if doc is a skill
            if any(skill.lower() in doc.lower() for skill in detected_skills):
                boost *= 2.0
            
            meta["boosted_score"] = meta["score"] * boost
            boosted.append((doc, meta))
        
        # Re-sort by boosted score
        boosted.sort(key=lambda x: x[1].get("boosted_score", x[1]["score"]), reverse=True)
        
        return boosted[:k]
    
    def get_statistics(self) -> Dict:
        """Get retrieval statistics."""
        return {
            "expansion_stats": dict(self.expansion_stats),
            "retrieval_stats": dict(self.retrieval_stats)
        }


# Testing
if __name__ == "__main__":
    import os
    
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    
    print("=" * 70)
    print("ADVANCED RETRIEVER TEST")
    print("=" * 70)
    
    retriever = AdvancedRetriever(
        db_path="doctors.db",
        vector_store_dir="./chroma_langchain_db",
        use_vector_store=has_api_key,
        verbose=True
    )
    
    test_queries = [
        "chest pain specialist",
        "bone doctor who does surgery",
        "skin laser therapy",
        "who does CBT",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        # Standard retrieval
        results = retriever.retrieve_advanced(query, k=5, top_expansions=5)
        print(f"\nTop 5 Results (Advanced):")
        for i, (doc, meta) in enumerate(results, 1):
            print(f"  {i}. {doc} (score: {meta['score']:.3f}, matches: {meta['match_count']})")
        
        # Skill-boosted retrieval
        print(f"\nTop 5 Results (Skill-Boosted):")
        skill_results = retriever.retrieve_with_skill_boost(query, k=5, top_expansions=5)
        for i, (doc, meta) in enumerate(skill_results, 1):
            score = meta.get("boosted_score", meta["score"])
            print(f"  {i}. {doc} (score: {score:.3f})")
