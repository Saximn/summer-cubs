"""
Production-Ready Retrieval Evaluation with Graded Relevance.

Features:
- Graded relevance (0-3 scale) instead of binary
- Detailed error analysis
- Side-by-side comparison of retrieval methods
- Performance tracking & benchmarking
- Resume-friendly metrics reporting
"""

import json
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import traceback

try:
    from hybrid_retrieval import HybridRetriever
    from sql_vector_retriever import SQLVectorRetriever
    from vector_utils import init_embeddings, init_vector_store, get_retriever
except ImportError:
    from .hybrid_retrieval import HybridRetriever
    from .sql_vector_retriever import SQLVectorRetriever
    from .vector_utils import init_embeddings, init_vector_store, get_retriever


class ProductionRetrievalEvaluator:
    """Production-ready retrieval evaluation with graded relevance."""
    
    def __init__(
        self,
        dataset_path: str = "evaluation_dataset_corrected.json",
        use_vector_store: bool = True,
        verbose: bool = True
    ):
        """
        Initialize evaluator.
        
        Args:
            dataset_path: Path to curated evaluation dataset
            use_vector_store: Whether to use vector store (requires API key)
            verbose: Print detailed output
        """
        self.dataset_path = dataset_path
        self.use_vector_store = use_vector_store
        self.verbose = verbose
        self.dataset = self._load_dataset()
        self.start_time = time.time()

    def _is_availability_query(self, query: str) -> bool:
        """Detect availability intent in a query."""
        query_lower = query.lower()
        keywords = [
            "available",
            "availability",
            "soon",
            "next",
            "schedule",
            "appointment",
            "book",
            "booking",
            "slot",
            "opening",
            "earliest",
            "soonest",
        ]
        return any(keyword in query_lower for keyword in keywords)
    
    def _load_dataset(self) -> Dict:
        """Load evaluation dataset from JSON."""
        dataset_file = Path(__file__).parent / self.dataset_path
        if not dataset_file.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_file}")
        
        with open(dataset_file, 'r') as f:
            return json.load(f)
    
    def _log(self, msg: str):
        """Print if verbose."""
        if self.verbose:
            print(msg)
    
    # ============================================================
    # GRADED RELEVANCE METRICS
    # ============================================================
    
    def get_relevance_grade(
        self,
        doc: str,
        relevant_docs: Dict[str, int]
    ) -> int:
        """
        Get relevance grade (0-3) for a document.
        
        Args:
            doc: Document to grade
            relevant_docs: Dict mapping doc -> grade (3=exact, 2=strong, 1=related, 0=none)
        
        Returns:
            Relevance grade (0-3)
        """
        # Exact match
        if doc in relevant_docs:
            return relevant_docs[doc]
        
        # Lowercase exact match
        if doc.lower() in {k.lower(): v for k, v in relevant_docs.items()}:
            return relevant_docs.get(doc.lower(), 2)
        
        # No match
        return 0
    
    def dcg_at_k(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        k: int
    ) -> float:
        """
        Calculate Discounted Cumulative Gain with graded relevance.
        
        DCG@K = Σ (rel_i / log2(i+1)) for i in [1, k]
        
        Args:
            retrieved_docs: List of retrieved documents
            relevance_grades: Dict mapping doc -> grade (0-3)
            k: Cutoff position
        
        Returns:
            DCG@K score
        """
        dcg = 0.0
        
        for i, doc in enumerate(retrieved_docs[:k], start=1):
            relevance = self.get_relevance_grade(doc, relevance_grades)
            dcg += relevance / np.log2(i + 1)
        
        return dcg
    
    def idcg_at_k(
        self,
        relevance_grades: Dict[str, int],
        k: int
    ) -> float:
        """
        Calculate Ideal DCG (perfect ranking).
        
        Args:
            relevance_grades: Dict mapping doc -> grade
            k: Cutoff position
        
        Returns:
            IDCG@K score
        """
        # Sort by relevance descending
        sorted_grades = sorted(relevance_grades.values(), reverse=True)
        idcg = 0.0
        
        for i, rel in enumerate(sorted_grades[:k], start=1):
            idcg += rel / np.log2(i + 1)
        
        return idcg
    
    def ndcg_at_k(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        k: int
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain.
        
        NDCG@K = DCG@K / IDCG@K
        
        Args:
            retrieved_docs: List of retrieved documents
            relevance_grades: Dict mapping doc -> grade
            k: Cutoff position
        
        Returns:
            NDCG@K score (0-1)
        """
        if not relevance_grades:
            return 0.0
        
        dcg = self.dcg_at_k(retrieved_docs, relevance_grades, k)
        idcg = self.idcg_at_k(relevance_grades, k)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def recall_at_k(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        k: int,
        min_grade: int = 2
    ) -> float:
        """
        Calculate Recall@K for documents with grade >= min_grade.
        
        Args:
            retrieved_docs: List of retrieved documents
            relevance_grades: Dict mapping doc -> grade
            k: Cutoff position
            min_grade: Minimum relevance grade to count (default: 2 = strong match)
        
        Returns:
            Recall@K score
        """
        # Count total relevant docs with grade >= min_grade
        total_relevant = sum(1 for g in relevance_grades.values() if g >= min_grade)
        
        if total_relevant == 0:
            return 0.0
        
        # Count retrieved relevant docs in top-k with grade >= min_grade
        retrieved_relevant = sum(
            1 for doc in retrieved_docs[:k]
            if self.get_relevance_grade(doc, relevance_grades) >= min_grade
        )
        
        return retrieved_relevant / total_relevant
    
    def precision_at_k(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        k: int,
        min_grade: int = 2
    ) -> float:
        """Calculate Precision@K."""
        if k == 0:
            return 0.0
        
        relevant_in_top_k = sum(
            1 for doc in retrieved_docs[:k]
            if self.get_relevance_grade(doc, relevance_grades) >= min_grade
        )
        
        return relevant_in_top_k / k
    
    def f1_at_k(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        k: int,
        min_grade: int = 2
    ) -> float:
        """Calculate F1@K (harmonic mean of precision and recall)."""
        precision = self.precision_at_k(retrieved_docs, relevance_grades, k, min_grade)
        recall = self.recall_at_k(retrieved_docs, relevance_grades, k, min_grade)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def mrr(
        self,
        retrieved_docs: List[str],
        relevance_grades: Dict[str, int],
        min_grade: int = 2
    ) -> float:
        """
        Calculate Mean Reciprocal Rank for docs with grade >= min_grade.
        
        Args:
            retrieved_docs: List of retrieved documents
            relevance_grades: Dict mapping doc -> grade
            min_grade: Minimum relevance grade to count
        
        Returns:
            MRR score
        """
        for rank, doc in enumerate(retrieved_docs, start=1):
            if self.get_relevance_grade(doc, relevance_grades) >= min_grade:
                return 1.0 / rank
        
        return 0.0
    
    # ============================================================
    # EVALUATION FRAMEWORK
    # ============================================================
    
    def evaluate_retriever(
        self,
        retriever_func,
        k_values: List[int] = [1, 3, 5, 10],
        retriever_name: str = "retriever",
        min_grade: int = 2
    ) -> Dict:
        """
        Evaluate a retriever on the curated dataset.
        
        Args:
            retriever_func: Function that takes (query, k) and returns list of docs
            k_values: List of K values to evaluate
            retriever_name: Name for reporting
            min_grade: Minimum relevance grade to count as "relevant"
        
        Returns:
            Comprehensive metrics dictionary
        """
        queries = self.dataset["queries"]
        results_by_difficulty = defaultdict(lambda: {
            "queries": [],
            "mrr_scores": [],
            "recall_scores": defaultdict(list),
            "precision_scores": defaultdict(list),
            "ndcg_scores": defaultdict(list),
            "f1_scores": defaultdict(list),
            "failed": 0
        })
        
        self._log(f"\n{'='*70}")
        self._log(f"EVALUATING: {retriever_name}")
        self._log(f"{'='*70}")
        self._log(f"Total queries: {len(queries)}")
        
        latencies = []
        failed_queries = []
        
        # Evaluate each query
        for i, query_data in enumerate(queries, 1):
            query = query_data["query"]
            difficulty = query_data.get("difficulty", "medium")
            max_k = max(k_values)
            
            try:
                # Retrieve documents
                start_time = time.time()
                retrieved_docs = retriever_func(query, max_k)
                latency = time.time() - start_time
                latencies.append(latency)
                
                # Get relevance grades
                relevance_grades = query_data.get("relevance_grades", {})
                
                # Calculate metrics
                mrr_score = self.mrr(retrieved_docs, relevance_grades, min_grade)
                results_by_difficulty[difficulty]["mrr_scores"].append(mrr_score)
                
                for k in k_values:
                    recall = self.recall_at_k(retrieved_docs, relevance_grades, k, min_grade)
                    precision = self.precision_at_k(retrieved_docs, relevance_grades, k, min_grade)
                    ndcg = self.ndcg_at_k(retrieved_docs, relevance_grades, k)
                    f1 = self.f1_at_k(retrieved_docs, relevance_grades, k, min_grade)
                    
                    results_by_difficulty[difficulty]["recall_scores"][k].append(recall)
                    results_by_difficulty[difficulty]["precision_scores"][k].append(precision)
                    results_by_difficulty[difficulty]["ndcg_scores"][k].append(ndcg)
                    results_by_difficulty[difficulty]["f1_scores"][k].append(f1)
                
                results_by_difficulty[difficulty]["queries"].append(query_data)
                
            except Exception as e:
                self._log(f"  [FAIL] Failed: {query[:50]}... | Error: {str(e)[:60]}")
                failed_queries.append({"query": query, "error": str(e)})
                results_by_difficulty[difficulty]["failed"] += 1
        
        # Aggregate metrics
        metrics = {
            "retriever": retriever_name,
            "total_queries": len(queries),
            "succeeded": len(queries) - len(failed_queries),
            "failed": len(failed_queries),
            "failure_rate": len(failed_queries) / len(queries) if queries else 0,
            "latency": {
                "mean": float(np.mean(latencies)) if latencies else 0,
                "median": float(np.median(latencies)) if latencies else 0,
                "p95": float(np.percentile(latencies, 95)) if latencies else 0,
                "p99": float(np.percentile(latencies, 99)) if latencies else 0
            },
            "overall": {},
            "by_difficulty": {}
        }
        
        # Aggregate overall metrics
        all_mrr = []
        overall_recall = defaultdict(list)
        overall_precision = defaultdict(list)
        overall_ndcg = defaultdict(list)
        overall_f1 = defaultdict(list)
        
        for difficulty, results in results_by_difficulty.items():
            # Overall aggregation
            all_mrr.extend(results["mrr_scores"])
            
            for k in k_values:
                overall_recall[k].extend(results["recall_scores"][k])
                overall_precision[k].extend(results["precision_scores"][k])
                overall_ndcg[k].extend(results["ndcg_scores"][k])
                overall_f1[k].extend(results["f1_scores"][k])
            
            # Per-difficulty aggregation
            metrics["by_difficulty"][difficulty] = {
                "num_queries": len(results["queries"]),
                "failed": results["failed"],
                "mrr": float(np.mean(results["mrr_scores"])) if results["mrr_scores"] else 0.0,
                "recall": {},
                "precision": {},
                "ndcg": {},
                "f1": {}
            }
            
            for k in k_values:
                metrics["by_difficulty"][difficulty]["recall"][f"@{k}"] = float(
                    np.mean(results["recall_scores"][k])
                ) if results["recall_scores"][k] else 0.0
                metrics["by_difficulty"][difficulty]["precision"][f"@{k}"] = float(
                    np.mean(results["precision_scores"][k])
                ) if results["precision_scores"][k] else 0.0
                metrics["by_difficulty"][difficulty]["ndcg"][f"@{k}"] = float(
                    np.mean(results["ndcg_scores"][k])
                ) if results["ndcg_scores"][k] else 0.0
                metrics["by_difficulty"][difficulty]["f1"][f"@{k}"] = float(
                    np.mean(results["f1_scores"][k])
                ) if results["f1_scores"][k] else 0.0
        
        # Overall metrics
        metrics["overall"] = {
            "mrr": float(np.mean(all_mrr)) if all_mrr else 0.0,
            "recall": {},
            "precision": {},
            "ndcg": {},
            "f1": {}
        }
        
        for k in k_values:
            metrics["overall"]["recall"][f"@{k}"] = float(
                np.mean(overall_recall[k])
            ) if overall_recall[k] else 0.0
            metrics["overall"]["precision"][f"@{k}"] = float(
                np.mean(overall_precision[k])
            ) if overall_precision[k] else 0.0
            metrics["overall"]["ndcg"][f"@{k}"] = float(
                np.mean(overall_ndcg[k])
            ) if overall_ndcg[k] else 0.0
            metrics["overall"]["f1"][f"@{k}"] = float(
                np.mean(overall_f1[k])
            ) if overall_f1[k] else 0.0
        
        # Print results
        self._print_metrics(metrics)
        
        return metrics

    def evaluate_availability(
        self,
        sql_vector_retriever,
        k_values: List[int] = [1, 3, 5, 10]
    ) -> Dict:
        """
        Evaluate availability-aware quality for SQL+vector retriever.

        Metrics:
        - availability_rate@k: fraction of results with a scheduled slot
        - same_day_rate@k: fraction of results available today
        - avg_days_until@k: mean days until next available slot (scheduled only)
        - availability_score@k: availability_rate@k * (1 / (1 + avg_days_until@k))
        """
        queries = self.dataset["queries"]
        availability_queries = [q for q in queries if self._is_availability_query(q["query"])]

        results_by_difficulty = defaultdict(lambda: {
            "availability_rate": defaultdict(list),
            "same_day_rate": defaultdict(list),
            "avg_days_until": defaultdict(list),
            "num_queries": 0,
        })

        for query_data in availability_queries:
            query = query_data["query"]
            difficulty = query_data.get("difficulty", "medium")
            max_k = max(k_values)

            results = sql_vector_retriever.retrieve(query, k=max_k)
            results_by_difficulty[difficulty]["num_queries"] += 1

            for k in k_values:
                top_k = results[:k]
                if not top_k:
                    results_by_difficulty[difficulty]["availability_rate"][k].append(0.0)
                    results_by_difficulty[difficulty]["same_day_rate"][k].append(0.0)
                    results_by_difficulty[difficulty]["avg_days_until"][k].append(0.0)
                    continue

                days = []
                same_day_count = 0
                available_count = 0
                for item in top_k:
                    next_avail = item.get("next_available", {})
                    days_until = next_avail.get("days_until")
                    if days_until is None:
                        continue

                    available_count += 1
                    days.append(days_until)
                    if days_until == 0:
                        same_day_count += 1

                availability_rate = available_count / k
                same_day_rate = same_day_count / k
                avg_days_until = float(np.mean(days)) if days else 0.0

                results_by_difficulty[difficulty]["availability_rate"][k].append(availability_rate)
                results_by_difficulty[difficulty]["same_day_rate"][k].append(same_day_rate)
                results_by_difficulty[difficulty]["avg_days_until"][k].append(avg_days_until)

        metrics = {
            "availability_queries": len(availability_queries),
            "overall": {
                "availability_rate": {},
                "same_day_rate": {},
                "avg_days_until": {},
                "availability_score": {},
            },
            "by_difficulty": {},
        }

        for k in k_values:
            all_rates = []
            all_same_day = []
            all_days = []
            for difficulty, diff in results_by_difficulty.items():
                all_rates.extend(diff["availability_rate"][k])
                all_same_day.extend(diff["same_day_rate"][k])
                all_days.extend(diff["avg_days_until"][k])

            overall_rate = float(np.mean(all_rates)) if all_rates else 0.0
            overall_same_day = float(np.mean(all_same_day)) if all_same_day else 0.0
            overall_avg_days = float(np.mean(all_days)) if all_days else 0.0
            overall_score = overall_rate * (1.0 / (1.0 + overall_avg_days)) if overall_rate > 0 else 0.0

            metrics["overall"]["availability_rate"][f"@{k}"] = overall_rate
            metrics["overall"]["same_day_rate"][f"@{k}"] = overall_same_day
            metrics["overall"]["avg_days_until"][f"@{k}"] = overall_avg_days
            metrics["overall"]["availability_score"][f"@{k}"] = overall_score

        for difficulty, diff in results_by_difficulty.items():
            metrics["by_difficulty"][difficulty] = {
                "num_queries": diff["num_queries"],
                "availability_rate": {},
                "same_day_rate": {},
                "avg_days_until": {},
                "availability_score": {},
            }
            for k in k_values:
                diff_rate = float(np.mean(diff["availability_rate"][k])) if diff["availability_rate"][k] else 0.0
                diff_same_day = float(np.mean(diff["same_day_rate"][k])) if diff["same_day_rate"][k] else 0.0
                diff_avg_days = float(np.mean(diff["avg_days_until"][k])) if diff["avg_days_until"][k] else 0.0
                diff_score = diff_rate * (1.0 / (1.0 + diff_avg_days)) if diff_rate > 0 else 0.0

                metrics["by_difficulty"][difficulty]["availability_rate"][f"@{k}"] = diff_rate
                metrics["by_difficulty"][difficulty]["same_day_rate"][f"@{k}"] = diff_same_day
                metrics["by_difficulty"][difficulty]["avg_days_until"][f"@{k}"] = diff_avg_days
                metrics["by_difficulty"][difficulty]["availability_score"][f"@{k}"] = diff_score

        return metrics
    
    def _print_metrics(self, metrics: Dict):
        """Print formatted metrics."""
        self._log("\n[RESULTS] OVERALL RESULTS:")
        self._log(f"   Success: {metrics['succeeded']}/{metrics['total_queries']} queries")
        self._log(f"   MRR: {metrics['overall']['mrr']:.4f}")
        self._log(f"   Latency: {metrics['latency']['mean']*1000:.1f}ms (p95: {metrics['latency']['p95']*1000:.1f}ms)")
        
        for k in [1, 3, 5, 10]:
            k_str = f"@{k}"
            if k_str in metrics["overall"]["recall"]:
                recall = metrics["overall"]["recall"][k_str]
                precision = metrics["overall"]["precision"].get(k_str, 0)
                ndcg = metrics["overall"]["ndcg"].get(k_str, 0)
                f1 = metrics["overall"]["f1"].get(k_str, 0)
                self._log(f"   Recall@{k}: {recall:.4f} | Precision@{k}: {precision:.4f} | NDCG@{k}: {ndcg:.4f} | F1@{k}: {f1:.4f}")
        
        self._log("\n[RESULTS] BY DIFFICULTY:")
        for difficulty in ["easy", "medium", "hard"]:
            if difficulty in metrics["by_difficulty"]:
                diff_metrics = metrics["by_difficulty"][difficulty]
                self._log(f"   {difficulty.upper()} ({diff_metrics['num_queries']} queries):")
                self._log(f"      MRR: {diff_metrics['mrr']:.4f}")
                self._log(f"      Recall@5: {diff_metrics['recall'].get('@5', 0):.4f}")
                self._log(f"      Recall@10: {diff_metrics['recall'].get('@10', 0):.4f}")
    
    def compare_retrievers(
        self,
        k_values: List[int] = [1, 3, 5, 10],
        min_grade: int = 2,
        save_results: bool = True
    ) -> Dict:
        """
        Compare multiple retrieval methods.
        
        Args:
            k_values: List of K values
            min_grade: Minimum relevance grade to count
            save_results: Save to JSON
        
        Returns:
            Comparison results
        """
        results = {
            "metadata": self.dataset["metadata"],
            "k_values": k_values,
            "min_grade": min_grade,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "evaluations": {},
            "comparison": {}
        }
        
        # Evaluate vector-only (baseline)
        if self.use_vector_store:
            try:
                embeddings = init_embeddings()
                vector_store = init_vector_store(
                    name="medical_collection",
                    embeddings=embeddings,
                    directory="./chroma_langchain_db"
                )
                
                def vector_retriever(query: str, k: int) -> List[str]:
                    result_docs = vector_store.similarity_search(query, k=k)
                    return [doc.page_content for doc in result_docs]
                
                vector_metrics = self.evaluate_retriever(
                    vector_retriever,
                    k_values=k_values,
                    retriever_name="Vector Only (Baseline)",
                    min_grade=min_grade
                )
                results["evaluations"]["vector"] = vector_metrics
            except Exception as e:
                self._log(f"[WARN] Vector evaluation failed: {e}")
        
        # Evaluate hybrid
        try:
            retriever = HybridRetriever(use_vector_store=self.use_vector_store)
            
            def hybrid_retriever(query: str, k: int) -> List[str]:
                result_docs = retriever.hybrid_search(query, k=k)
                return [doc for doc, _ in result_docs]
            
            hybrid_metrics = self.evaluate_retriever(
                hybrid_retriever,
                k_values=k_values,
                retriever_name="Hybrid (BM25 + Vector Rerank)",
                min_grade=min_grade
            )
            results["evaluations"]["hybrid"] = hybrid_metrics
        except Exception as e:
            self._log(f"[WARN] Hybrid evaluation failed: {e}")

        # Evaluate SQL + vector + schedule-aware retriever
        try:
            sql_vector = SQLVectorRetriever(use_vector_store=self.use_vector_store)

            def sql_vector_retriever(query: str, k: int) -> List[str]:
                results = sql_vector.retrieve(query, k=k)
                specialties = []
                skills = []

                for result in results:
                    specialty = result.get("specialty")
                    if specialty:
                        specialties.append(specialty)

                    for skill in result.get("skills", []):
                        skills.append(skill)

                flattened = specialties + skills

                seen = set()
                deduped = []
                for item in flattened:
                    if item not in seen:
                        seen.add(item)
                        deduped.append(item)
                return deduped[:k]

            sql_vector_metrics = self.evaluate_retriever(
                sql_vector_retriever,
                k_values=k_values,
                retriever_name="SQL + Vector + Schedule",
                min_grade=min_grade
            )
            availability_metrics = self.evaluate_availability(
                sql_vector,
                k_values=k_values,
            )
            sql_vector_metrics["availability"] = availability_metrics
            self._log("\n[RESULTS] AVAILABILITY-AWARE METRICS:")
            self._log(f"   Availability intent queries: {availability_metrics['availability_queries']}")
            for k in k_values:
                rate = availability_metrics["overall"]["availability_rate"].get(f"@{k}", 0)
                same_day = availability_metrics["overall"]["same_day_rate"].get(f"@{k}", 0)
                avg_days = availability_metrics["overall"]["avg_days_until"].get(f"@{k}", 0)
                score = availability_metrics["overall"]["availability_score"].get(f"@{k}", 0)
                self._log(
                    f"   Availability@{k}: {rate:.4f} | Same-day@{k}: {same_day:.4f} | Avg days@{k}: {avg_days:.2f} | Score@{k}: {score:.4f}"
                )
            results["evaluations"]["sql_vector"] = sql_vector_metrics
        except Exception as e:
            self._log(f"[WARN] SQL+vector evaluation failed: {e}")
        
        # Generate comparison
        if "vector" in results["evaluations"] and "hybrid" in results["evaluations"]:
            results["comparison"] = self._generate_comparison(
                results["evaluations"]["vector"],
                results["evaluations"]["hybrid"],
                results["evaluations"].get("sql_vector"),
                k_values
            )
        
        # Save results
        if save_results:
            output_path = Path(__file__).parent / "retrieval_metrics_production.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            self._log(f"\n[OK] Results saved to: {output_path}")
        
        return results
    
    def _generate_comparison(
        self,
        vector_metrics: Dict,
        hybrid_metrics: Dict,
        sql_vector_metrics: Optional[Dict],
        k_values: List[int]
    ) -> Dict:
        """Generate comparison between retrievers."""
        comparison = {}
        
        # Overall comparison
        comparison["summary"] = {
            "vector_recall@10": vector_metrics["overall"]["recall"].get("@10", 0),
            "hybrid_recall@10": hybrid_metrics["overall"]["recall"].get("@10", 0),
            "recall_improvement_pct": 0,
            "vector_mrr": vector_metrics["overall"]["mrr"],
            "hybrid_mrr": hybrid_metrics["overall"]["mrr"],
            "mrr_improvement_pct": 0,
            "sql_vector_recall@10": None,
            "sql_vector_mrr": None,
            "sql_vector_recall_improvement_pct": None,
            "sql_vector_mrr_improvement_pct": None
        }
        
        # Calculate improvements
        baseline_r10 = vector_metrics["overall"]["recall"].get("@10", 1)
        if baseline_r10 > 0:
            improvement = (
                (hybrid_metrics["overall"]["recall"].get("@10", 0) - baseline_r10) 
                / baseline_r10 * 100
            )
            comparison["summary"]["recall_improvement_pct"] = improvement
        
        baseline_mrr = vector_metrics["overall"]["mrr"]
        if baseline_mrr > 0:
            mrr_improvement = (
                (hybrid_metrics["overall"]["mrr"] - baseline_mrr) 
                / baseline_mrr * 100
            )
            comparison["summary"]["mrr_improvement_pct"] = mrr_improvement

        if sql_vector_metrics:
            comparison["summary"]["sql_vector_recall@10"] = sql_vector_metrics["overall"]["recall"].get("@10", 0)
            comparison["summary"]["sql_vector_mrr"] = sql_vector_metrics["overall"]["mrr"]

            if baseline_r10 > 0:
                comparison["summary"]["sql_vector_recall_improvement_pct"] = (
                    (comparison["summary"]["sql_vector_recall@10"] - baseline_r10) / baseline_r10 * 100
                )

            if baseline_mrr > 0:
                comparison["summary"]["sql_vector_mrr_improvement_pct"] = (
                    (comparison["summary"]["sql_vector_mrr"] - baseline_mrr) / baseline_mrr * 100
                )
        
        # Detailed by metric
        comparison["by_metric"] = {}
        for k in k_values:
            k_str = f"@{k}"
            comparison["by_metric"][f"recall@{k}"] = {
                "vector": vector_metrics["overall"]["recall"].get(k_str, 0),
                "hybrid": hybrid_metrics["overall"]["recall"].get(k_str, 0),
                "improvement_pct": 0
            }
            
            baseline = vector_metrics["overall"]["recall"].get(k_str, 1)
            if baseline > 0:
                comparison["by_metric"][f"recall@{k}"]["improvement_pct"] = (
                    (hybrid_metrics["overall"]["recall"].get(k_str, 0) - baseline) / baseline * 100
                )
        
        return comparison


if __name__ == "__main__":
    import os
    
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    
    print("="*70)
    print("PRODUCTION RETRIEVAL EVALUATION")
    print("="*70)
    
    evaluator = ProductionRetrievalEvaluator(
        dataset_path="evaluation_dataset_corrected.json",
        use_vector_store=has_api_key,
        verbose=True
    )
    
    results = evaluator.compare_retrievers(
        k_values=[1, 3, 5, 10],
        min_grade=2,
        save_results=True
    )
    
    # Print improvement summary
    if "comparison" in results:
        summary = results["comparison"].get("summary", {})
        print("\n" + "="*70)
        print("[SUMMARY] IMPROVEMENT SUMMARY (for resume)")
        print("="*70)
        print(f"Recall@10 (Hybrid): {summary.get('vector_recall@10', 0):.1%} -> {summary.get('hybrid_recall@10', 0):.1%} ({summary.get('recall_improvement_pct', 0):+.1f}%)")
        print(f"MRR (Hybrid): {summary.get('vector_mrr', 0):.4f} -> {summary.get('hybrid_mrr', 0):.4f} ({summary.get('mrr_improvement_pct', 0):+.1f}%)")
        if summary.get("sql_vector_recall@10") is not None:
            print(f"Recall@10 (SQL+Vector): {summary.get('vector_recall@10', 0):.1%} -> {summary.get('sql_vector_recall@10', 0):.1%} ({summary.get('sql_vector_recall_improvement_pct', 0):+.1f}%)")
            print(f"MRR (SQL+Vector): {summary.get('vector_mrr', 0):.4f} -> {summary.get('sql_vector_mrr', 0):.4f} ({summary.get('sql_vector_mrr_improvement_pct', 0):+.1f}%)")
            availability = results.get("evaluations", {}).get("sql_vector", {}).get("availability", {})
            availability_score = availability.get("overall", {}).get("availability_score", {})
            if availability_score:
                print(f"Availability Score@10 (SQL+Vector): {availability_score.get('@10', 0):.4f}")
        print("="*70)

