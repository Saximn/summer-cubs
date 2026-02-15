# HospitalIQ Chatbot Evaluation System

Comprehensive evaluation framework for the LangGraph-based medical chatbot with metrics for retrieval, latency, and accuracy.

## 📊 Overview

The evaluation system provides:
- **Retrieval Evaluation**: Offline evaluation with Recall@K, MRR, and NDCG metrics
- **Hybrid Retrieval**: Two-stage BM25 + vector reranking system
- **Chatbot Performance**: Latency (P50/P95/P99) and accuracy metrics
- **Automated Pipeline**: Complete evaluation workflow with comprehensive reporting

## 🏗️ Architecture

```
backend/chatbot/
├── generate_test_data.py       # Generate test queries from database
├── evaluation_dataset.json     # Curated test dataset (105 queries)
├── hybrid_retrieval.py         # BM25 + vector hybrid search
├── evaluate_retrieval.py       # Retrieval metrics (Recall, MRR, NDCG)
├── evaluate_chatbot.py         # Chatbot latency & accuracy
├── run_evaluation.py           # Main evaluation pipeline
├── retrieval_metrics.json      # Retrieval results
├── chatbot_metrics.json        # Chatbot performance results
└── evaluation_results.json     # Complete evaluation report
```

## 🚀 Quick Start

### 1. Generate Test Data (Optional)

```bash
cd backend/chatbot
python generate_test_data.py
```

This generates `evaluation_dataset.json` with 100+ test queries based on your database.

### 2. Run Complete Evaluation

```bash
# Full evaluation (requires OPENAI_API_KEY)
export OPENAI_API_KEY=your_key_here
python run_evaluation.py

# With limited queries (faster)
python run_evaluation.py --max-queries 50

# Regenerate dataset before evaluation
python run_evaluation.py --regenerate
```

### 3. Run Individual Evaluations

```bash
# Retrieval evaluation only (no API key needed for BM25)
python evaluate_retrieval.py

# Chatbot performance (requires API key)
python evaluate_chatbot.py

# Test hybrid retrieval
python hybrid_retrieval.py
```

## 📈 Evaluation Metrics

### Retrieval Metrics

#### Recall@K
Measures the percentage of relevant documents retrieved in top K results.

```
Recall@K = |relevant_docs ∩ retrieved_docs[:k]| / |relevant_docs|
```

**Typical values:**
- Recall@1: 0.85-0.90
- Recall@10: 0.85-0.95

#### Mean Reciprocal Rank (MRR)
Average of 1/rank of first relevant document. Higher is better.

```
MRR = average(1 / rank_of_first_relevant_doc)
```

**Target:** MRR > 0.7

#### NDCG (Normalized Discounted Cumulative Gain)
Graded relevance scoring with position discount.

```
NDCG@K = DCG@K / IDCG@K
```

**Target:** NDCG@10 > 0.8

### Latency Metrics

- **P50 (Median)**: 50% of queries complete within this time
- **P95**: 95% of queries complete within this time
- **P99**: 99% of queries complete within this time

**Success Criteria:**
- P95 < 5 seconds for database queries
- P99 < 10 seconds for complex queries

### Accuracy Metrics

- **Routing Accuracy**: % of queries correctly routed (database vs general)
  - **Target:** > 95%
- **SQL Success Rate**: % of valid SQL queries generated
  - **Target:** > 90%

## 🔀 Hybrid Retrieval System

### Two-Stage Approach

1. **Stage 1: BM25 Lexical Search**
   - Fast keyword-based retrieval
   - Retrieves top-50 candidates
   - Good for exact term matching

2. **Stage 2: Vector Reranking**
   - Semantic similarity using embeddings
   - Reranks BM25 results
   - Returns final top-10 results

### Usage in Code

```python
from hybrid_retrieval import HybridRetriever

# Initialize
retriever = HybridRetriever(
    db_path="doctors.db",
    bm25_k=50,  # Stage 1 candidates
    final_k=10   # Final results
)

# Search
results = retriever.hybrid_search("cardiology surgery", k=5)
for doc, score in results:
    print(f"{doc}: {score:.3f}")
```

### Integration with Chatbot

Enable hybrid retrieval when initializing the chatbot:

```python
from langgraph_chatbot import LangGraphChatbot

# With hybrid retrieval
bot = LangGraphChatbot(use_hybrid_retrieval=True)

# Default (vector-only)
bot = LangGraphChatbot()
```

## 📝 Test Dataset Format

The evaluation dataset (`evaluation_dataset.json`) contains:

```json
{
  "metadata": {
    "total_queries": 105,
    "database_queries": 99,
    "general_queries": 6,
    "query_types": ["count", "specialty", "skill_search", ...]
  },
  "queries": [
    {
      "query": "How many doctors specialize in cardiology?",
      "relevant_docs": ["cardiology"],
      "expected_route": "database",
      "ground_truth_answer": "There are X doctors...",
      "query_type": "specialty_count",
      "sql_pattern": "SELECT COUNT(*) FROM doctors WHERE specialty = 'cardiology'"
    }
  ]
}
```

### Query Types

- **count**: Simple count queries
- **specialty_count/list**: Specialty-based queries
- **skill_search**: Skill-based doctor search
- **complex_join**: Multi-table joins
- **general_definition**: Medical definitions (no DB)
- **datetime**: Time/date queries
- **greeting**: Casual conversation

## 📊 Sample Results

### Baseline (BM25 Only)

```
Retrieval Performance:
  Recall@10: 0.8710 | MRR: 0.8710 | NDCG@10: 0.8710

Chatbot Performance:
  P50: 2.1s | P95: 4.8s | P99: 7.2s
  Routing Accuracy: 96.5%
  SQL Success Rate: 92.3%
```

### With Hybrid Retrieval (BM25 + Vector)

```
Retrieval Performance:
  Recall@10: 0.9245 | MRR: 0.9102 | NDCG@10: 0.9180
  Improvement: +5.4%

Chatbot Performance:
  P50: 2.3s | P95: 5.1s | P99: 7.8s
  Routing Accuracy: 97.2%
  SQL Success Rate: 94.1%
```

## 🎯 Success Criteria

The evaluation system checks the following criteria:

- ✅ **P95 latency < 5 seconds** for database queries
- ✅ **Routing accuracy > 95%**
- ✅ **Recall@10 improvement >= 5%** with hybrid retrieval
- ✅ **MRR > 0.7** on retrieval tasks
- ✅ **Zero crashes** during evaluation

## 🔧 Configuration

### Environment Variables

```bash
# Required for full evaluation
export OPENAI_API_KEY=your_api_key

# Optional: Change database path
export DB_PATH=path/to/doctors.db
```

### Evaluation Parameters

Customize evaluation in `run_evaluation.py`:

```python
pipeline = EvaluationPipeline(
    dataset_path="evaluation_dataset.json",
    regenerate_dataset=False  # Set True to regenerate
)

results = pipeline.run_full_pipeline(
    max_chatbot_queries=100,  # Limit queries for faster testing
    save_results=True
)
```

## 📁 Output Files

### retrieval_metrics.json
Detailed retrieval evaluation results:
```json
{
  "baseline": { "recall": {...}, "mrr": 0.87 },
  "hybrid": { "recall": {...}, "mrr": 0.91 },
  "improvement": { "recall@10_pct": 5.4 }
}
```

### chatbot_metrics.json
Chatbot performance metrics:
```json
{
  "metrics": {
    "latency": { "p50": 2.1, "p95": 4.8, "p99": 7.2 },
    "routing_accuracy": { "accuracy_pct": 96.5 },
    "sql_success": { "success_rate_pct": 92.3 }
  }
}
```

### evaluation_results.json
Complete evaluation report with summary and success criteria.

## 🐛 Troubleshooting

### No API Key Error

**Solution:** The evaluation system supports BM25-only mode without an API key. Only vector operations require OPENAI_API_KEY.

```bash
# Run without API key (BM25 only)
python evaluate_retrieval.py
```

### Database Not Found

**Solution:** Ensure `doctors.db` exists in the chatbot directory:

```bash
cd backend/chatbot
python populate_db.py  # Regenerate database
```

### Slow Evaluation

**Solution:** Limit the number of queries:

```bash
python run_evaluation.py --max-queries 20
```

## 🔍 Extending the System

### Add New Metrics

1. Edit `evaluate_chatbot.py` or `evaluate_retrieval.py`
2. Add your metric calculation function
3. Include in `run_full_evaluation()`

### Add Custom Test Queries

Edit `generate_test_data.py` to add more query patterns:

```python
custom_queries = [
    {
        "query": "Your custom query",
        "relevant_docs": ["doc1", "doc2"],
        "expected_route": "database",
        "query_type": "custom_type"
    }
]
test_queries.extend(custom_queries)
```

### Customize Hybrid Retrieval

Adjust weights in `hybrid_retrieval.py`:

```python
# Current: BM25 40%, Vector 60%
combined_score = 0.4 * bm25_norm + 0.6 * vector_score

# More weight to BM25 (lexical)
combined_score = 0.6 * bm25_norm + 0.4 * vector_score
```

## 📚 References

- **BM25**: Best Match 25 ranking function for information retrieval
- **MRR**: Mean Reciprocal Rank for ranking evaluation
- **NDCG**: Normalized Discounted Cumulative Gain for graded relevance
- **LangGraph**: Framework for building stateful, multi-actor applications with LLMs

## 🤝 Contributing

When adding new features:
1. Update test dataset with relevant queries
2. Run evaluation to measure impact
3. Document baseline vs improved metrics
4. Update this README with new metrics/features

---

**Last Updated:** 2026-02-15
**Version:** 1.0.0
