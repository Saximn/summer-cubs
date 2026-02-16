#!/usr/bin/env python3
"""Generate comprehensive evaluation report comparing all three retrieval methods."""

import json
from pathlib import Path

# Results from the evaluation runs
results = {
    "dataset": "evaluation_dataset_corrected.json",
    "total_queries": 39,
    "easy_queries": 10,
    "medium_queries": 15,
    "hard_queries": 14,
    "timestamp": "2024",
    "retrievers": {
        "vector_only": {
            "name": "Vector Embedding Only (Baseline)",
            "recall_at_10": 0.9487,
            "mrr": 0.9145,
            "latency_ms": 172.6,
            "p95_latency_ms": 230.3,
            "by_difficulty": {
                "easy": {"recall_at_10": 1.0000, "mrr": 1.0000},
                "medium": {"recall_at_10": 0.8667, "mrr": 0.8778},
                "hard": {"recall_at_10": 1.0000, "mrr": 0.8929}
            }
        },
        "hybrid": {
            "name": "Hybrid (BM25 + Vector)",
            "recall_at_10": 0.6923,
            "mrr": 0.8504,
            "latency_ms": 173.3,
            "p95_latency_ms": 193.7,
            "by_difficulty": {
                "easy": {"recall_at_10": 1.0000, "mrr": 1.0000},
                "medium": {"recall_at_10": 0.4667, "mrr": 0.8111},
                "hard": {"recall_at_10": 0.7143, "mrr": 0.7857}
            },
            "note": "BM25 is limited by small corpus (40 docs)"
        },
        "advanced_multi_stage": {
            "name": "Advanced Multi-Stage Retriever",
            "recall_at_10": 0.8850,
            "mrr": 0.9103,
            "latency_ms": 780.0,
            "p95_latency_ms": 1202.3,
            "by_difficulty": {
                "easy": {"recall_at_10": 1.0000, "mrr": 1.0000},
                "medium": {"recall_at_10": 0.7667, "mrr": 0.8333},
                "hard": {"recall_at_10": 0.9286, "mrr": 0.9286}
            },
            "note": "Query expansion + multi-stage retrieval with skill boosting"
        }
    }
}

print("="*80)
print("COMPREHENSIVE RETRIEVAL EVALUATION REPORT")
print("="*80)
print()

print(f"Dataset: {results['dataset']}")
print(f"Total Queries: {results['total_queries']} (Easy: {results['easy_queries']}, Medium: {results['medium_queries']}, Hard: {results['hard_queries']})")
print()

print("="*80)
print("OVERALL PERFORMANCE COMPARISON")
print("="*80)
print()

header = f"{'Method':<35} {'Recall@10':<15} {'MRR':<12} {'Latency (ms)':<15} {'P95 (ms)':<10}"
print(header)
print("-"*80)

for key, retriever in results['retrievers'].items():
    name = retriever['name']
    recall = f"{retriever['recall_at_10']:.1%}"
    mrr = f"{retriever['mrr']:.4f}"
    latency = f"{retriever['latency_ms']:.1f}"
    p95 = f"{retriever['p95_latency_ms']:.1f}"
    print(f"{name:<35} {recall:<15} {mrr:<12} {latency:<15} {p95:<10}")

print()
print("="*80)
print("ANALYSIS BY DIFFICULTY")
print("="*80)
print()

for difficulty in ['easy', 'medium', 'hard']:
    print(f"\n{difficulty.upper()} QUERIES:")
    print(f"  {'Method':<35} {'Recall@10':<15} {'MRR':<12}")
    print(f"  {'-'*60}")
    
    for key, retriever in results['retrievers'].items():
        if difficulty in retriever['by_difficulty']:
            recall = f"{retriever['by_difficulty'][difficulty]['recall_at_10']:.1%}"
            mrr = f"{retriever['by_difficulty'][difficulty]['mrr']:.4f}"
            print(f"  {retriever['name']:<35} {recall:<15} {mrr:<12}")

print()
print("="*80)
print("KEY FINDINGS")
print("="*80)
print()

print("1. BASELINE PERFORMANCE (Vector Embedding):")
print("   - Achieves 94.9% Recall@10 on realistic test set")
print("   - Fast and efficient (172.6ms average)")
print("   - Perfect performance on EASY queries (100%)")
print("   - Solid performance across difficulty levels")
print()

print("2. HYBRID APPROACH (BM25 + Vector):")
print("   - Underperforms at 69.2% Recall@10")
print("   - Limited by small BM25 corpus (40 documents = skills + specialties)")
print("   - BM25 struggles with semantic queries")
print("   - Similar latency to vector-only baseline")
print()

print("3. ADVANCED MULTI-STAGE RETRIEVER:")
print("   - Achieves 88.5% Recall@10 (-6.4% vs baseline)")
print("   - Excellent on HARD queries (92.9%) - typos, synonyms, abbreviations")
print("   - Perfect on EASY direct searches (100%)")
print("   - Much higher latency (780ms) due to query expansion overhead")
print("   - Uses sophisticated query expansion (synonyms, abbreviations, typo correction)")
print()

print("="*80)
print("RECOMMENDATIONS")
print("="*80)
print()

print("IMMEDIATE:")
print("  [1] Vector-only baseline is highly effective (94.9% Recall)")
print("  [2] For production: Use vector-only for speed-critical applications")
print("  [3] Advanced retriever better for complex queries, but 4.5x slower")
print()

print("OPTIMIZATION OPPORTUNITIES:")
print("  [1] Reduce advanced retriever latency:")
print("      - Cache query expansions")
print("      - Use approximate nearest neighbors (ANNs) for vector search")
print("      - Parallel query expansion processing")
print()
print("  [2] Enhance hybrid approach:")
print("      - Expand BM25 corpus beyond 40 documents")
print("      - Add synonyms/skill descriptions to index")
print("      - Use learning-to-rank for better weighting")
print()
print("  [3] Create specialized pipelines:")
print("      - Use vector-only for simple specialty/skill searches")
print("      - Use advanced retriever when typo/synonym correction needed")
print("      - Hybrid approach only for specific use cases")
print()

print("="*80)
print("DATASET QUALITY NOTES")
print("="*80)
print()

print("This evaluation used a CORRECTED dataset with realistic expectations:")
print("  - All expected results are actual database contents")
print("  - 10 realistic specialties, 30 actual skills")
print("  - No synthetic/impossible expectations (like 'cardiac' when only 'cardiology' exists)")
print("  - Properly represents actual retrieval task")
print()

# Save full results to JSON
output_path = Path(__file__).parent / "evaluation_comprehensive_report.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] Full results saved to: {output_path}")
