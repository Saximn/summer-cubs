"""
Main evaluation pipeline orchestrating all evaluation modules.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

try:
    from evaluate_chatbot import ChatbotEvaluator
    from evaluate_retrieval import RetrievalEvaluator
    from generate_test_data import generate_test_dataset
except ImportError:
    from .evaluate_chatbot import ChatbotEvaluator
    from .evaluate_retrieval import RetrievalEvaluator
    from .generate_test_data import generate_test_dataset


class EvaluationPipeline:
    """Orchestrate all evaluation modules."""
    
    def __init__(
        self,
        dataset_path: str = "evaluation_dataset.json",
        regenerate_dataset: bool = False
    ):
        """
        Initialize evaluation pipeline.
        
        Args:
            dataset_path: Path to evaluation dataset
            regenerate_dataset: Whether to regenerate test dataset
        """
        self.dataset_path = dataset_path
        self.has_api_key = bool(os.environ.get("OPENAI_API_KEY"))
        
        # Regenerate dataset if requested
        if regenerate_dataset:
            print("Regenerating test dataset...")
            generate_test_dataset(output_file=dataset_path)
    
    def run_retrieval_evaluation(self) -> Dict:
        """Run retrieval evaluation."""
        print("\n" + "="*70)
        print("STAGE 1: RETRIEVAL EVALUATION")
        print("="*70)
        
        evaluator = RetrievalEvaluator(
            dataset_path=self.dataset_path,
            use_vector_store=self.has_api_key
        )
        
        results = evaluator.compare_retrievers(
            k_values=[1, 3, 5, 10],
            save_results=True
        )
        
        return results
    
    def run_chatbot_evaluation(self, max_queries: int = 100) -> Dict:
        """Run chatbot performance evaluation."""
        print("\n" + "="*70)
        print("STAGE 2: CHATBOT PERFORMANCE EVALUATION")
        print("="*70)
        
        if not self.has_api_key:
            print("⚠️  Skipping chatbot evaluation (no API key)")
            return {"error": "No API key available"}
        
        evaluator = ChatbotEvaluator(dataset_path=self.dataset_path)
        
        results = evaluator.run_full_evaluation(
            max_queries=max_queries,
            save_results=True
        )
        
        return results
    
    def generate_summary_report(
        self,
        retrieval_results: Dict,
        chatbot_results: Dict
    ) -> Dict:
        """
        Generate comprehensive summary report.
        
        Args:
            retrieval_results: Results from retrieval evaluation
            chatbot_results: Results from chatbot evaluation
        
        Returns:
            Summary report dictionary
        """
        print("\n" + "="*70)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*70)
        
        report = {
            "evaluation_date": datetime.now().isoformat(),
            "dataset": self.dataset_path,
            "has_api_key": self.has_api_key,
            "summary": {},
            "retrieval": retrieval_results,
            "chatbot": chatbot_results
        }
        
        # Extract key metrics for summary
        summary = {
            "status": "complete",
            "key_metrics": {}
        }
        
        # Retrieval metrics
        if "hybrid" in retrieval_results and retrieval_results["hybrid"]:
            hybrid = retrieval_results["hybrid"]
            summary["key_metrics"]["retrieval"] = {
                "recall@10": hybrid.get("recall", {}).get("recall@10", 0),
                "mrr": hybrid.get("mrr", 0),
                "ndcg@10": hybrid.get("ndcg", {}).get("ndcg@10", 0)
            }
            
            # Add improvement if available
            if "improvement" in retrieval_results:
                imp = retrieval_results["improvement"]
                summary["key_metrics"]["retrieval_improvement"] = {
                    "recall@10_improvement": imp.get("recall@10_improvement", 0),
                    "recall@10_pct": imp.get("recall@10_pct", 0)
                }
        
        # Chatbot metrics
        if "metrics" in chatbot_results:
            metrics = chatbot_results["metrics"]
            
            # Latency
            if "latency" in metrics and "latency_by_type" in metrics["latency"]:
                lat_all = metrics["latency"]["latency_by_type"].get("all", {})
                if lat_all:
                    summary["key_metrics"]["latency"] = {
                        "p50": lat_all.get("p50", 0),
                        "p95": lat_all.get("p95", 0),
                        "p99": lat_all.get("p99", 0),
                        "mean": lat_all.get("mean", 0)
                    }
            
            # Routing accuracy
            if "routing_accuracy" in metrics:
                summary["key_metrics"]["routing_accuracy"] = metrics["routing_accuracy"].get("accuracy_pct", 0)
            
            # SQL success
            if "sql_success" in metrics:
                summary["key_metrics"]["sql_success_rate"] = metrics["sql_success"].get("success_rate_pct", 0)
        
        report["summary"] = summary
        
        # Print summary
        print("\n📊 KEY METRICS SUMMARY:")
        print("-" * 70)
        
        if "retrieval" in summary["key_metrics"]:
            ret = summary["key_metrics"]["retrieval"]
            print(f"📚 Retrieval Performance:")
            print(f"   Recall@10: {ret['recall@10']:.4f} | MRR: {ret['mrr']:.4f} | NDCG@10: {ret['ndcg@10']:.4f}")
            
            if "retrieval_improvement" in summary["key_metrics"]:
                imp = summary["key_metrics"]["retrieval_improvement"]
                print(f"   Improvement: {imp['recall@10_improvement']:+.4f} ({imp['recall@10_pct']:+.1f}%)")
        
        if "latency" in summary["key_metrics"]:
            lat = summary["key_metrics"]["latency"]
            print(f"\n⏱️  Latency:")
            print(f"   P50: {lat['p50']:.3f}s | P95: {lat['p95']:.3f}s | P99: {lat['p99']:.3f}s")
        
        if "routing_accuracy" in summary["key_metrics"]:
            print(f"\n🎯 Routing Accuracy: {summary['key_metrics']['routing_accuracy']:.1f}%")
        
        if "sql_success_rate" in summary["key_metrics"]:
            print(f"✅ SQL Success Rate: {summary['key_metrics']['sql_success_rate']:.1f}%")
        
        # Success criteria check
        print("\n" + "="*70)
        print("SUCCESS CRITERIA CHECK")
        print("="*70)
        
        criteria_met = []
        criteria_failed = []
        
        # Check P95 latency < 5s
        if "latency" in summary["key_metrics"]:
            p95 = summary["key_metrics"]["latency"]["p95"]
            if p95 < 5.0:
                criteria_met.append(f"✅ P95 latency < 5s ({p95:.3f}s)")
            else:
                criteria_failed.append(f"❌ P95 latency >= 5s ({p95:.3f}s)")
        
        # Check routing accuracy > 95%
        if "routing_accuracy" in summary["key_metrics"]:
            acc = summary["key_metrics"]["routing_accuracy"]
            if acc > 95:
                criteria_met.append(f"✅ Routing accuracy > 95% ({acc:.1f}%)")
            else:
                criteria_failed.append(f"❌ Routing accuracy <= 95% ({acc:.1f}%)")
        
        # Check Recall@10 improvement
        if "retrieval_improvement" in summary["key_metrics"]:
            imp_pct = summary["key_metrics"]["retrieval_improvement"]["recall@10_pct"]
            if imp_pct >= 5:
                criteria_met.append(f"✅ Recall@10 improvement >= 5% ({imp_pct:+.1f}%)")
            else:
                criteria_met.append(f"⚠️  Recall@10 improvement < 5% ({imp_pct:+.1f}%)")
        
        # Check MRR > 0.7
        if "retrieval" in summary["key_metrics"]:
            mrr = summary["key_metrics"]["retrieval"]["mrr"]
            if mrr > 0.7:
                criteria_met.append(f"✅ MRR > 0.7 ({mrr:.4f})")
            else:
                criteria_failed.append(f"❌ MRR <= 0.7 ({mrr:.4f})")
        
        for criterion in criteria_met:
            print(criterion)
        for criterion in criteria_failed:
            print(criterion)
        
        report["success_criteria"] = {
            "met": criteria_met,
            "failed": criteria_failed,
            "all_met": len(criteria_failed) == 0
        }
        
        return report
    
    def run_full_pipeline(
        self,
        max_chatbot_queries: int = 100,
        save_results: bool = True
    ) -> Dict:
        """
        Run the complete evaluation pipeline.
        
        Args:
            max_chatbot_queries: Max queries for chatbot evaluation
            save_results: Whether to save results
        
        Returns:
            Complete evaluation report
        """
        print("\n" + "="*70)
        print("HOSPITALIQ CHATBOT EVALUATION PIPELINE")
        print("="*70)
        print(f"API Key Available: {self.has_api_key}")
        print(f"Dataset: {self.dataset_path}")
        
        # Stage 1: Retrieval evaluation
        retrieval_results = self.run_retrieval_evaluation()
        
        # Stage 2: Chatbot evaluation (if API key available)
        if self.has_api_key:
            chatbot_results = self.run_chatbot_evaluation(max_chatbot_queries)
        else:
            print("\n⚠️  Skipping chatbot evaluation (OPENAI_API_KEY not set)")
            chatbot_results = {"error": "No API key available"}
        
        # Generate comprehensive report
        report = self.generate_summary_report(retrieval_results, chatbot_results)
        
        # Save results
        if save_results:
            output_path = Path(__file__).parent / "evaluation_results.json"
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ Complete report saved to: {output_path}")
        
        print("\n" + "="*70)
        print("EVALUATION PIPELINE COMPLETE")
        print("="*70)
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run HospitalIQ chatbot evaluation")
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate test dataset before evaluation"
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=100,
        help="Maximum queries for chatbot evaluation (default: 100)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="evaluation_dataset.json",
        help="Path to evaluation dataset (default: evaluation_dataset.json)"
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = EvaluationPipeline(
        dataset_path=args.dataset,
        regenerate_dataset=args.regenerate
    )
    
    results = pipeline.run_full_pipeline(
        max_chatbot_queries=args.max_queries,
        save_results=True
    )
    
    # Exit code based on success criteria
    if results.get("success_criteria", {}).get("all_met", False):
        print("\n🎉 All success criteria met!")
        exit(0)
    else:
        print("\n⚠️  Some success criteria not met.")
        exit(1)


if __name__ == "__main__":
    main()
