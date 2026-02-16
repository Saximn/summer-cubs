#!/usr/bin/env python3
"""Test the advanced retriever against aligned dataset."""

import json
import time
import numpy as np
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

try:
    from retrieval_advanced import AdvancedRetriever
    from evaluate_retrieval_production import ProductionRetrievalEvaluator
except ImportError:
    from .retrieval_advanced import AdvancedRetriever
    from .evaluate_retrieval_production import ProductionRetrievalEvaluator


def evaluate_advanced_retriever():
    """Evaluate advanced retriever with graded relevance."""
    
    # Load aligned dataset
    dataset_path = Path(__file__).parent / "evaluation_dataset_corrected.json"
    if not dataset_path.exists():
        print(f"[ERROR] Dataset not found: {dataset_path}")
        return
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    print("="*70)
    print("ADVANCED RETRIEVER EVALUATION (Aligned Dataset)")
    print("="*70)
    print(f"Total queries: {len(dataset['queries'])}")
    print(f"Easy: {len([q for q in dataset['queries'] if q.get('difficulty') == 'easy'])}")
    print(f"Medium: {len([q for q in dataset['queries'] if q.get('difficulty') == 'medium'])}")
    print(f"Hard: {len([q for q in dataset['queries'] if q.get('difficulty') == 'hard'])}")
    print()
    
    # Initialize advanced retriever
    try:
        retriever = AdvancedRetriever()
        print("[OK] Advanced retriever initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize advanced retriever: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Evaluate retriever
    k_values = [1, 3, 5, 10]
    results_by_difficulty = defaultdict(lambda: {
        'total': 0,
        'success': 0,
        'metrics': defaultdict(lambda: defaultdict(list))
    })
    
    overall_metrics = {k: [] for k in k_values}
    latencies = []
    
    for query_idx, query_obj in enumerate(dataset['queries'], 1):  # Test all queries
        query = query_obj.get('query', '')
        difficulty = query_obj.get('difficulty', 'unknown')
        relevance_grades = query_obj.get('relevance_grades', {})
        
        results_by_difficulty[difficulty]['total'] += 1
        
        try:
            # Retrieve results
            start = time.time()
            results = retriever.retrieve_with_skill_boost(query, k=10)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
            
            results_by_difficulty[difficulty]['success'] += 1
            
            # Calculate metrics for each K
            for k in k_values:
                top_k_results = results[:k]
                retrieved_docs = set(r[0] for r in top_k_results)
                
                # Calculate recall (% of relevant docs in top-k)
                relevant_docs = set(doc for doc, grade in relevance_grades.items() if grade >= 2)
                if relevant_docs:
                    recall = len(retrieved_docs & relevant_docs) / len(relevant_docs)
                else:
                    recall = 1.0  # If no relevant docs, perfect score
                
                # Calculate precision (% of retrieved that are relevant)
                if retrieved_docs:
                    precision = len(retrieved_docs & relevant_docs) / len(retrieved_docs)
                else:
                    precision = 0.0
                
                # Calculate NDCG (ranking quality)
                dcg = 0.0
                idcg = 0.0
                for rank, (doc, _) in enumerate(top_k_results, 1):
                    grade = relevance_grades.get(doc, 0)
                    dcg += grade / np.log2(rank + 1)
                
                for rank, grade in enumerate(sorted(relevance_grades.values(), reverse=True)[:k], 1):
                    idcg += grade / np.log2(rank + 1)
                
                ndcg = dcg / idcg if idcg > 0 else 0.0
                
                # MRR (position of first relevant)
                mrr = 0.0
                for rank, (doc, _) in enumerate(top_k_results, 1):
                    if relevance_grades.get(doc, 0) >= 2:
                        mrr = 1.0 / rank
                        break
                
                results_by_difficulty[difficulty]['metrics'][k]['recall'].append(recall)
                results_by_difficulty[difficulty]['metrics'][k]['precision'].append(precision)
                results_by_difficulty[difficulty]['metrics'][k]['ndcg'].append(ndcg)
                results_by_difficulty[difficulty]['metrics'][k]['mrr'].append(mrr)
                overall_metrics[k].append({
                    'recall': recall,
                    'precision': precision,
                    'ndcg': ndcg,
                    'mrr': mrr
                })
        
        except Exception as e:
            print(f"[ERROR] Query {query_idx} ({difficulty}): {e}")
    
    # Print results
    print("\n" + "="*70)
    print("OVERALL RESULTS:")
    print("="*70)
    
    for k in k_values:
        metrics = overall_metrics[k]
        if metrics:
            recalls = [m['recall'] for m in metrics]
            precisions = [m['precision'] for m in metrics]
            ndcgs = [m['ndcg'] for m in metrics]
            mrrs = [m['mrr'] for m in metrics]
            
            print(f"\nK={k}:")
            print(f"  Recall@{k}: {np.mean(recalls):.1%} | Precision@{k}: {np.mean(precisions):.1%}")
            print(f"  NDCG@{k}: {np.mean(ndcgs):.4f} | MRR: {np.mean(mrrs):.4f}")
    
    print(f"\nLatency: {np.mean(latencies):.1f}ms (p95: {np.percentile(latencies, 95):.1f}ms)")
    
    # Results by difficulty
    print("\n" + "="*70)
    print("BY DIFFICULTY:")
    print("="*70)
    
    for difficulty in ['easy', 'medium', 'hard']:
        if difficulty not in results_by_difficulty:
            continue
        
        stats = results_by_difficulty[difficulty]
        print(f"\n{difficulty.upper()} ({stats['success']}/{stats['total']} successful):")
        
        k = 10
        if k in stats['metrics']:
            recalls = stats['metrics'][k]['recall']
            mrrs = stats['metrics'][k]['mrr']
            if recalls:
                print(f"  Recall@10: {np.mean(recalls):.1%}")
                print(f"  MRR: {np.mean(mrrs):.4f}")


if __name__ == "__main__":
    evaluate_advanced_retriever()
