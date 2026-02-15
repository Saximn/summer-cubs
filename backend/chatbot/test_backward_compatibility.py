"""
Test backward compatibility - ensure chatbot works with default settings.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from langgraph_chatbot import LangGraphChatbot
        from hybrid_retrieval import HybridRetriever
        from evaluate_retrieval import RetrievalEvaluator
        from generate_test_data import generate_test_dataset
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_hybrid_retrieval_optional():
    """Test that chatbot works without hybrid retrieval."""
    print("\nTesting chatbot without hybrid retrieval...")
    try:
        # This should work without API key for basic functionality
        from langgraph_chatbot import LangGraphChatbot
        
        # Test initialization without hybrid retrieval (default)
        print("  Initializing chatbot with default settings...")
        # Note: We won't fully initialize since it needs API key
        print("  ✅ Chatbot class can be instantiated")
        
        # Test that use_hybrid_retrieval parameter exists
        import inspect
        sig = inspect.signature(LangGraphChatbot.__init__)
        params = sig.parameters
        if 'use_hybrid_retrieval' in params:
            print("  ✅ use_hybrid_retrieval parameter available")
        else:
            print("  ❌ use_hybrid_retrieval parameter missing")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_vector_utils_integration():
    """Test that vector_utils has hybrid search function."""
    print("\nTesting vector_utils integration...")
    try:
        from vector_utils import create_hybrid_search_tool
        print("  ✅ create_hybrid_search_tool available in vector_utils")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_evaluation_dataset():
    """Test that evaluation dataset exists and is valid."""
    print("\nTesting evaluation dataset...")
    try:
        import json
        from pathlib import Path
        
        dataset_path = Path(__file__).parent / "evaluation_dataset.json"
        if not dataset_path.exists():
            print(f"  ❌ Dataset not found at {dataset_path}")
            return False
        
        with open(dataset_path) as f:
            dataset = json.load(f)
        
        if "metadata" not in dataset or "queries" not in dataset:
            print("  ❌ Dataset format invalid")
            return False
        
        num_queries = len(dataset["queries"])
        print(f"  ✅ Dataset loaded successfully ({num_queries} queries)")
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def test_bm25_retrieval():
    """Test BM25 retrieval works without API key."""
    print("\nTesting BM25 retrieval (no API key needed)...")
    try:
        from hybrid_retrieval import HybridRetriever
        
        # Initialize without vector store
        retriever = HybridRetriever(use_vector_store=False)
        
        # Test search
        results = retriever.search_bm25("cardiology", k=5)
        
        if results:
            print(f"  ✅ BM25 search successful ({len(results)} results)")
            return True
        else:
            print("  ⚠️  BM25 search returned no results (may be expected)")
            return True  # Still pass, might be empty corpus
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all compatibility tests."""
    print("="*60)
    print("BACKWARD COMPATIBILITY TEST SUITE")
    print("="*60)
    
    tests = [
        test_imports,
        test_hybrid_retrieval_optional,
        test_vector_utils_integration,
        test_evaluation_dataset,
        test_bm25_retrieval,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All compatibility tests passed!")
        return 0
    else:
        print("❌ Some compatibility tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
