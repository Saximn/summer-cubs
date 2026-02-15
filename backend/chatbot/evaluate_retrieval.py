"""
Offline retrieval evaluation with Recall@K, MRR, and NDCG metrics.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from hybrid_retrieval import HybridRetriever
    from vector_utils import init_embeddings, init_vector_store, get_retriever
except ImportError:
    from .hybrid_retrieval import HybridRetriever
    from .vector_utils import init_embeddings, init_vector_store, get_retriever


class RetrievalEvaluator:
    """Evaluate retrieval systems with standard IR metrics."""
    
    def __init__(
        self,
        dataset_path: str = "evaluation_dataset.json",
        use_vector_store: bool = True
    ):
        """
        Initialize evaluator.
        
        Args:
            dataset_path: Path to evaluation dataset JSON
            use_vector_store: Whether to use vector store (requires API key)
        """
        self.dataset_path = dataset_path
        self.use_vector_store = use_vector_store
        self.dataset = self._load_dataset()
    
    def _load_dataset(self) -> Dict:
        """Load evaluation dataset from JSON."""
        dataset_file = Path(__file__).parent / self.dataset_path
        with open(dataset_file, 'r') as f:
            return json.load(f)
    
    def recall_at_k(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        k: int
    ) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = |relevant_docs ∩ retrieved_docs[:k]| / |relevant_docs|
        
        Args:
            retrieved_docs: List of retrieved documents
            relevant_docs: List of relevant documents
            k: Cutoff position
        
        Returns:
            Recall@K score
        """
        if not relevant_docs:
            return 0.0
        
        retrieved_at_k = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        
        intersection = retrieved_at_k & relevant_set
        recall = len(intersection) / len(relevant_set)
        
        return recall
    
    def mean_reciprocal_rank(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str]
    ) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).
        
        MRR = 1 / rank_of_first_relevant_doc
        
        Args:
            retrieved_docs: List of retrieved documents
            relevant_docs: List of relevant documents
        
        Returns:
            MRR score (0 if no relevant doc found)
        """
        if not relevant_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        
        for rank, doc in enumerate(retrieved_docs, start=1):
            if doc in relevant_set:
                return 1.0 / rank
        
        return 0.0  # No relevant document found
    
    def dcg_at_k(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        k: int
    ) -> float:
        """
        Calculate Discounted Cumulative Gain at K.
        
        DCG@K = Σ (rel_i / log2(i+1)) for i in [1, k]
        
        Args:
            retrieved_docs: List of retrieved documents
            relevant_docs: List of relevant documents
            k: Cutoff position
        
        Returns:
            DCG@K score
        """
        if not relevant_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        dcg = 0.0
        
        for i, doc in enumerate(retrieved_docs[:k], start=1):
            relevance = 1 if doc in relevant_set else 0
            dcg += relevance / np.log2(i + 1)
        
        return dcg
    
    def ndcg_at_k(
        self,
        retrieved_docs: List[str],
        relevant_docs: List[str],
        k: int
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at K.
        
        NDCG@K = DCG@K / IDCG@K
        
        Args:
            retrieved_docs: List of retrieved documents
            relevant_docs: List of relevant documents
            k: Cutoff position
        
        Returns:
            NDCG@K score
        """
        if not relevant_docs:
            return 0.0
        
        # Calculate DCG
        dcg = self.dcg_at_k(retrieved_docs, relevant_docs, k)
        
        # Calculate IDCG (Ideal DCG - all relevant docs at top)
        ideal_retrieved = relevant_docs + [f"dummy_{i}" for i in range(k)]
        idcg = self.dcg_at_k(ideal_retrieved, relevant_docs, k)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_retriever(
        self,
        retriever_func,
        k_values: List[int] = [1, 3, 5, 10],
        retriever_name: str = "retriever"
    ) -> Dict:
        """
        Evaluate a retriever on the dataset.
        
        Args:
            retriever_func: Function that takes (query, k) and returns list of docs
            k_values: List of K values to evaluate
            retriever_name: Name of the retriever for reporting
        
        Returns:
            Dictionary with evaluation metrics
        """
        queries = self.dataset["queries"]
        
        # Filter to queries with relevant docs
        queries_with_relevance = [
            q for q in queries 
            if q.get("relevant_docs") and len(q["relevant_docs"]) > 0
        ]
        
        if not queries_with_relevance:
            print(f"⚠️  No queries with relevant docs found in dataset")
            return {}
        
        print(f"\n{'='*60}")
        print(f"Evaluating {retriever_name}")
        print(f"{'='*60}")
        print(f"Total queries with relevance judgments: {len(queries_with_relevance)}")
        
        # Initialize metrics storage
        metrics = {
            "retriever": retriever_name,
            "num_queries": len(queries_with_relevance),
            "recall": {},
            "mrr": 0.0,
            "ndcg": {}
        }
        
        # Evaluate each query
        all_mrr = []
        recall_at_k_all = {k: [] for k in k_values}
        ndcg_at_k_all = {k: [] for k in k_values}
        
        for query_data in queries_with_relevance:
            query = query_data["query"]
            relevant_docs = query_data["relevant_docs"]
            
            # Get max k for retrieval
            max_k = max(k_values)
            
            try:
                # Retrieve documents
                retrieved_docs = retriever_func(query, max_k)
                
                # Calculate MRR
                mrr = self.mean_reciprocal_rank(retrieved_docs, relevant_docs)
                all_mrr.append(mrr)
                
                # Calculate Recall@K and NDCG@K for each K
                for k in k_values:
                    recall = self.recall_at_k(retrieved_docs, relevant_docs, k)
                    recall_at_k_all[k].append(recall)
                    
                    ndcg = self.ndcg_at_k(retrieved_docs, relevant_docs, k)
                    ndcg_at_k_all[k].append(ndcg)
                    
            except Exception as e:
                print(f"Error evaluating query '{query}': {e}")
                # Add zeros for failed queries
                all_mrr.append(0.0)
                for k in k_values:
                    recall_at_k_all[k].append(0.0)
                    ndcg_at_k_all[k].append(0.0)
        
        # Calculate average metrics
        metrics["mrr"] = np.mean(all_mrr) if all_mrr else 0.0
        
        for k in k_values:
            metrics["recall"][f"recall@{k}"] = np.mean(recall_at_k_all[k]) if recall_at_k_all[k] else 0.0
            metrics["ndcg"][f"ndcg@{k}"] = np.mean(ndcg_at_k_all[k]) if ndcg_at_k_all[k] else 0.0
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   MRR: {metrics['mrr']:.4f}")
        for k in k_values:
            recall_val = metrics["recall"][f"recall@{k}"]
            ndcg_val = metrics["ndcg"][f"ndcg@{k}"]
            print(f"   Recall@{k}: {recall_val:.4f} | NDCG@{k}: {ndcg_val:.4f}")
        
        return metrics
    
    def evaluate_vector_only(self, k_values: List[int] = [1, 3, 5, 10]) -> Dict:
        """Evaluate pure vector retrieval."""
        if not self.use_vector_store:
            print("⚠️  Vector store not available, skipping evaluation")
            return {}
        
        try:
            # Initialize vector store
            embeddings = init_embeddings()
            vector_store = init_vector_store(
                name="medical_collection",
                embeddings=embeddings,
                directory="./chroma_langchain_db"
            )
            
            def vector_retriever(query: str, k: int) -> List[str]:
                """Retrieve using vector similarity."""
                results = vector_store.similarity_search(query, k=k)
                return [doc.page_content for doc in results]
            
            return self.evaluate_retriever(
                vector_retriever,
                k_values=k_values,
                retriever_name="Vector Only (Baseline)"
            )
        except Exception as e:
            print(f"⚠️  Vector evaluation failed: {e}")
            return {}
    
    def evaluate_hybrid(self, k_values: List[int] = [1, 3, 5, 10]) -> Dict:
        """Evaluate hybrid BM25 + vector retrieval."""
        try:
            # Initialize hybrid retriever
            retriever = HybridRetriever(use_vector_store=self.use_vector_store)
            
            def hybrid_retriever(query: str, k: int) -> List[str]:
                """Retrieve using hybrid approach."""
                results = retriever.hybrid_search(query, k=k)
                return [doc for doc, _ in results]
            
            retriever_name = "Hybrid (BM25 + Vector)" if self.use_vector_store else "BM25 Only"
            return self.evaluate_retriever(
                hybrid_retriever,
                k_values=k_values,
                retriever_name=retriever_name
            )
        except Exception as e:
            print(f"⚠️  Hybrid evaluation failed: {e}")
            return {}
    
    def compare_retrievers(
        self,
        k_values: List[int] = [1, 3, 5, 10],
        save_results: bool = True
    ) -> Dict:
        """
        Compare baseline (vector) vs hybrid retrieval.
        
        Args:
            k_values: List of K values to evaluate
            save_results: Whether to save results to JSON
        
        Returns:
            Comparison results
        """
        results = {
            "dataset": self.dataset_path,
            "total_queries": self.dataset["metadata"]["total_queries"],
            "k_values": k_values,
            "baseline": {},
            "hybrid": {},
            "improvement": {}
        }
        
        # Evaluate baseline (vector only)
        if self.use_vector_store:
            baseline_metrics = self.evaluate_vector_only(k_values)
            results["baseline"] = baseline_metrics
        
        # Evaluate hybrid
        hybrid_metrics = self.evaluate_hybrid(k_values)
        results["hybrid"] = hybrid_metrics
        
        # Calculate improvements
        if self.use_vector_store and results["baseline"] and results["hybrid"]:
            print(f"\n{'='*60}")
            print("IMPROVEMENT ANALYSIS")
            print(f"{'='*60}")
            
            for k in k_values:
                baseline_recall = results["baseline"]["recall"].get(f"recall@{k}", 0)
                hybrid_recall = results["hybrid"]["recall"].get(f"recall@{k}", 0)
                improvement = hybrid_recall - baseline_recall
                pct_improvement = (improvement / baseline_recall * 100) if baseline_recall > 0 else 0
                
                results["improvement"][f"recall@{k}_improvement"] = improvement
                results["improvement"][f"recall@{k}_pct"] = pct_improvement
                
                print(f"Recall@{k}: {baseline_recall:.4f} → {hybrid_recall:.4f} "
                      f"({improvement:+.4f}, {pct_improvement:+.1f}%)")
            
            baseline_mrr = results["baseline"]["mrr"]
            hybrid_mrr = results["hybrid"]["mrr"]
            mrr_improvement = hybrid_mrr - baseline_mrr
            mrr_pct = (mrr_improvement / baseline_mrr * 100) if baseline_mrr > 0 else 0
            
            results["improvement"]["mrr_improvement"] = mrr_improvement
            results["improvement"]["mrr_pct"] = mrr_pct
            
            print(f"MRR: {baseline_mrr:.4f} → {hybrid_mrr:.4f} "
                  f"({mrr_improvement:+.4f}, {mrr_pct:+.1f}%)")
        
        # Save results
        if save_results:
            output_path = Path(__file__).parent / "retrieval_metrics.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✅ Results saved to: {output_path}")
        
        return results


if __name__ == "__main__":
    import os
    
    # Check if API key is available
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    
    print("="*60)
    print("RETRIEVAL EVALUATION")
    print("="*60)
    print(f"Using vector store: {has_api_key}")
    
    # Initialize evaluator
    evaluator = RetrievalEvaluator(use_vector_store=has_api_key)
    
    # Run comparison
    results = evaluator.compare_retrievers(
        k_values=[1, 3, 5, 10],
        save_results=True
    )
    
    print("\n✅ Evaluation complete!")
