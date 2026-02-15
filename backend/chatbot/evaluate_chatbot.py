"""
Comprehensive chatbot performance evaluation with latency and accuracy metrics.
"""

import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import traceback

try:
    from langgraph_chatbot import LangGraphChatbot
except ImportError:
    from .langgraph_chatbot import LangGraphChatbot


class ChatbotEvaluator:
    """Evaluate chatbot performance with latency and accuracy metrics."""
    
    def __init__(
        self,
        dataset_path: str = "evaluation_dataset.json",
        timeout: float = 10.0
    ):
        """
        Initialize evaluator.
        
        Args:
            dataset_path: Path to evaluation dataset
            timeout: Timeout for individual queries (seconds)
        """
        self.dataset_path = dataset_path
        self.timeout = timeout
        self.dataset = self._load_dataset()
        self.chatbot = None
    
    def _load_dataset(self) -> Dict:
        """Load evaluation dataset from JSON."""
        dataset_file = Path(__file__).parent / self.dataset_path
        with open(dataset_file, 'r') as f:
            return json.load(f)
    
    def _init_chatbot(self):
        """Initialize chatbot if not already initialized."""
        if self.chatbot is None:
            print("Initializing chatbot...")
            self.chatbot = LangGraphChatbot()
    
    def measure_latency(
        self,
        queries: List[Dict],
        max_queries: int = None
    ) -> Dict:
        """
        Measure latency metrics (P50, P95, P99) for queries.
        
        Args:
            queries: List of query dictionaries
            max_queries: Maximum number of queries to test (None = all)
        
        Returns:
            Dictionary with latency statistics
        """
        self._init_chatbot()
        
        # Limit queries if needed
        test_queries = queries[:max_queries] if max_queries else queries
        
        print(f"\n{'='*60}")
        print(f"LATENCY EVALUATION")
        print(f"{'='*60}")
        print(f"Testing {len(test_queries)} queries...")
        
        # Group queries by type
        query_groups = {
            "general": [],
            "database": [],
            "datetime": []
        }
        
        latencies_by_type = {
            "general": [],
            "database": [],
            "datetime": [],
            "all": []
        }
        
        failed_queries = []
        
        # Test each query
        for i, query_data in enumerate(test_queries, 1):
            query = query_data["query"]
            expected_route = query_data.get("expected_route", "general")
            query_type = query_data.get("query_type", "unknown")
            
            # Determine group
            if "datetime" in query_type:
                group = "datetime"
            elif expected_route == "database":
                group = "database"
            else:
                group = "general"
            
            try:
                # Measure latency
                start_time = time.time()
                response = self.chatbot.ask(query)
                latency = time.time() - start_time
                
                # Store latency
                latencies_by_type[group].append(latency)
                latencies_by_type["all"].append(latency)
                
                if i % 10 == 0:
                    print(f"  Processed {i}/{len(test_queries)} queries...")
                
            except Exception as e:
                print(f"  ⚠️  Query failed: {query[:50]}... Error: {str(e)[:100]}")
                failed_queries.append({
                    "query": query,
                    "error": str(e),
                    "type": group
                })
        
        # Calculate statistics
        results = {
            "total_queries": len(test_queries),
            "successful_queries": len(latencies_by_type["all"]),
            "failed_queries": len(failed_queries),
            "failure_rate": len(failed_queries) / len(test_queries) if test_queries else 0,
            "latency_by_type": {},
            "overall_latency": {}
        }
        
        # Calculate percentiles for each type
        for group, latencies in latencies_by_type.items():
            if latencies:
                results["latency_by_type"][group] = {
                    "count": len(latencies),
                    "mean": float(np.mean(latencies)),
                    "median": float(np.median(latencies)),
                    "p50": float(np.percentile(latencies, 50)),
                    "p95": float(np.percentile(latencies, 95)),
                    "p99": float(np.percentile(latencies, 99)),
                    "min": float(np.min(latencies)),
                    "max": float(np.max(latencies))
                }
        
        # Print results
        print(f"\n📊 Latency Results:")
        print(f"   Total queries: {results['total_queries']}")
        print(f"   Successful: {results['successful_queries']}")
        print(f"   Failed: {results['failed_queries']} ({results['failure_rate']*100:.1f}%)")
        
        for group, stats in results["latency_by_type"].items():
            if stats:
                print(f"\n   {group.upper()} queries ({stats['count']}):")
                print(f"      P50: {stats['p50']:.3f}s | P95: {stats['p95']:.3f}s | P99: {stats['p99']:.3f}s")
                print(f"      Mean: {stats['mean']:.3f}s | Min: {stats['min']:.3f}s | Max: {stats['max']:.3f}s")
        
        results["failed_queries_details"] = failed_queries
        
        return results
    
    def evaluate_routing_accuracy(self, queries: List[Dict]) -> Dict:
        """
        Evaluate routing accuracy (database vs general).
        
        Args:
            queries: List of query dictionaries
        
        Returns:
            Dictionary with routing accuracy metrics
        """
        self._init_chatbot()
        
        print(f"\n{'='*60}")
        print(f"ROUTING ACCURACY EVALUATION")
        print(f"{'='*60}")
        
        correct_routes = 0
        total_routes = 0
        routing_details = []
        
        for query_data in queries:
            query = query_data["query"]
            expected_route = query_data.get("expected_route", "general")
            
            try:
                # Analyze query routing (simulating the chatbot's analyze step)
                initial_state = {
                    "messages": [],
                    "user_query": query,
                    "needs_database": False,
                    "database_result": "",
                    "final_answer": ""
                }
                
                # Run analysis
                analyzed_state = self.chatbot._analyze_query(initial_state)
                actual_route = "database" if analyzed_state["needs_database"] else "general"
                
                is_correct = (actual_route == expected_route)
                if is_correct:
                    correct_routes += 1
                total_routes += 1
                
                routing_details.append({
                    "query": query,
                    "expected": expected_route,
                    "actual": actual_route,
                    "correct": is_correct
                })
                
            except Exception as e:
                print(f"  ⚠️  Routing check failed for: {query[:50]}...")
                routing_details.append({
                    "query": query,
                    "expected": expected_route,
                    "actual": "error",
                    "correct": False,
                    "error": str(e)
                })
        
        accuracy = correct_routes / total_routes if total_routes > 0 else 0
        
        results = {
            "total_queries": total_routes,
            "correct_routes": correct_routes,
            "incorrect_routes": total_routes - correct_routes,
            "accuracy": accuracy,
            "accuracy_pct": accuracy * 100,
            "details": routing_details
        }
        
        # Print results
        print(f"\n📊 Routing Accuracy:")
        print(f"   Total: {total_routes}")
        print(f"   Correct: {correct_routes}/{total_routes} ({accuracy*100:.1f}%)")
        print(f"   Incorrect: {total_routes - correct_routes}")
        
        # Show some examples of incorrect routing
        incorrect = [d for d in routing_details if not d.get("correct", False)]
        if incorrect:
            print(f"\n   Sample incorrect routings:")
            for detail in incorrect[:5]:
                print(f"      '{detail['query'][:40]}...' -> Expected: {detail['expected']}, Got: {detail['actual']}")
        
        return results
    
    def evaluate_sql_success_rate(self, queries: List[Dict]) -> Dict:
        """
        Evaluate SQL query success rate for database queries.
        
        Args:
            queries: List of query dictionaries
        
        Returns:
            Dictionary with SQL success metrics
        """
        self._init_chatbot()
        
        print(f"\n{'='*60}")
        print(f"SQL SUCCESS RATE EVALUATION")
        print(f"{'='*60}")
        
        # Filter to database queries only
        db_queries = [q for q in queries if q.get("expected_route") == "database"]
        
        print(f"Testing {len(db_queries)} database queries...")
        
        successful_sql = 0
        total_sql = 0
        sql_details = []
        
        for query_data in db_queries:
            query = query_data["query"]
            
            try:
                # Try to execute the query
                response = self.chatbot.ask(query)
                
                # Check if response indicates success (not an error message)
                has_error = any(err in response.lower() for err in [
                    "error", "couldn't", "unable", "failed", "trouble", "sorry"
                ])
                
                is_success = not has_error and len(response) > 10
                
                if is_success:
                    successful_sql += 1
                total_sql += 1
                
                sql_details.append({
                    "query": query,
                    "success": is_success,
                    "response_length": len(response),
                    "response_preview": response[:100] if is_success else response
                })
                
            except Exception as e:
                total_sql += 1
                sql_details.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        success_rate = successful_sql / total_sql if total_sql > 0 else 0
        
        results = {
            "total_sql_queries": total_sql,
            "successful_queries": successful_sql,
            "failed_queries": total_sql - successful_sql,
            "success_rate": success_rate,
            "success_rate_pct": success_rate * 100,
            "details": sql_details
        }
        
        # Print results
        print(f"\n📊 SQL Success Rate:")
        print(f"   Total: {total_sql}")
        print(f"   Successful: {successful_sql}/{total_sql} ({success_rate*100:.1f}%)")
        print(f"   Failed: {total_sql - successful_sql}")
        
        return results
    
    def run_full_evaluation(
        self,
        max_queries: int = None,
        save_results: bool = True
    ) -> Dict:
        """
        Run full evaluation suite.
        
        Args:
            max_queries: Maximum queries per metric (None = all)
            save_results: Whether to save results to JSON
        
        Returns:
            Complete evaluation results
        """
        print("\n" + "="*60)
        print("CHATBOT PERFORMANCE EVALUATION")
        print("="*60)
        print(f"Dataset: {self.dataset_path}")
        print(f"Total queries in dataset: {self.dataset['metadata']['total_queries']}")
        print(f"Testing up to {max_queries if max_queries else 'all'} queries per metric")
        
        queries = self.dataset["queries"]
        test_queries = queries[:max_queries] if max_queries else queries
        
        results = {
            "evaluation_date": datetime.now().isoformat(),
            "dataset": self.dataset_path,
            "total_queries_in_dataset": len(queries),
            "queries_tested": len(test_queries),
            "metrics": {}
        }
        
        # 1. Latency evaluation
        try:
            latency_results = self.measure_latency(test_queries)
            results["metrics"]["latency"] = latency_results
        except Exception as e:
            print(f"\n⚠️  Latency evaluation failed: {e}")
            traceback.print_exc()
            results["metrics"]["latency"] = {"error": str(e)}
        
        # 2. Routing accuracy
        try:
            routing_results = self.evaluate_routing_accuracy(test_queries)
            results["metrics"]["routing_accuracy"] = routing_results
        except Exception as e:
            print(f"\n⚠️  Routing evaluation failed: {e}")
            traceback.print_exc()
            results["metrics"]["routing_accuracy"] = {"error": str(e)}
        
        # 3. SQL success rate
        try:
            sql_results = self.evaluate_sql_success_rate(test_queries)
            results["metrics"]["sql_success"] = sql_results
        except Exception as e:
            print(f"\n⚠️  SQL evaluation failed: {e}")
            traceback.print_exc()
            results["metrics"]["sql_success"] = {"error": str(e)}
        
        # Save results
        if save_results:
            output_path = Path(__file__).parent / "chatbot_metrics.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✅ Results saved to: {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        if "latency" in results["metrics"] and "overall_latency" in results["metrics"]["latency"]:
            lat = results["metrics"]["latency"]["latency_by_type"].get("all", {})
            if lat:
                print(f"⏱️  Latency (all queries):")
                print(f"   P50: {lat['p50']:.3f}s | P95: {lat['p95']:.3f}s | P99: {lat['p99']:.3f}s")
        
        if "routing_accuracy" in results["metrics"]:
            acc = results["metrics"]["routing_accuracy"].get("accuracy_pct", 0)
            print(f"🎯 Routing Accuracy: {acc:.1f}%")
        
        if "sql_success" in results["metrics"]:
            sql_rate = results["metrics"]["sql_success"].get("success_rate_pct", 0)
            print(f"✅ SQL Success Rate: {sql_rate:.1f}%")
        
        return results


if __name__ == "__main__":
    import os
    
    # Check if API key is available
    has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
    
    if not has_api_key:
        print("⚠️  OPENAI_API_KEY not set. Evaluation may fail.")
        print("   Set the API key to run full evaluation.")
    
    # Initialize evaluator
    evaluator = ChatbotEvaluator()
    
    # Run evaluation (limit to 50 queries for testing)
    results = evaluator.run_full_evaluation(
        max_queries=50,
        save_results=True
    )
    
    print("\n✅ Evaluation complete!")
