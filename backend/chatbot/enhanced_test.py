"""
Enhanced test script for the LangGraph chatbot with better visualization.
"""

from langgraph_chatbot import LangGraphChatbot
import time


def test_conditional_flow_enhanced():
    """Test the conditional flow with clear visual separation."""
    print("🚀 Initializing LangGraph Medical Chatbot...")
    bot = LangGraphChatbot()
    
    test_cases = [
        {
            "category": "General Conversation",
            "expected_route": "general",
            "icon": "💬",
            "queries": [
                "Hello, how are you today?",
                "What is diabetes?", 
                "Can you explain how the heart works?",
                "Thank you for your help!"
            ]
        },
        {
            "category": "Database Queries", 
            "expected_route": "database",
            "icon": "🔍",
            "queries": [
                "How many doctors do we have?",
                "How many doctors specialize in cardiology?",
                "List all available specialties",
                "Find doctors with surgery skills"
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"{test_case['icon']} {test_case['category'].upper()} (Expected: {test_case['expected_route']})")
        print(f"{'='*60}")
        
        for query in test_case["queries"]:
            print(f"\n📝 Query: {query}")
            print("🤖 Processing...")
            
            start_time = time.time()
            response = bot.ask(query)
            end_time = time.time()
            
            print(f"✅ Response: {response}")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            print("-" * 40)


def interactive_demo():
    """Run an interactive demo session."""
    print("🎯 LangGraph Medical Chatbot - Interactive Demo")
    print("=" * 50)
    print("I'll automatically determine whether to:")
    print("🔍 Query the medical database")
    print("💬 Provide general conversation")
    print("\nType 'quit' to exit, 'demo' for sample queries")
    
    bot = LangGraphChatbot()
    
    sample_queries = [
        "How many cardiologists do we have?",
        "What is hypertension?", 
        "List all specialties",
        "Hello there!"
    ]
    
    while True:
        user_input = input("\n🔥 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'demo':
            print("\n🎪 Running demo queries...")
            for query in sample_queries:
                print(f"\n📝 Demo Query: {query}")
                print(f"🤖 Response: {bot.ask(query)}")
            continue
        elif not user_input:
            continue
            
        print(f"🤖 Bot: {bot.ask(user_input)}")


def main():
    """Main function to choose test mode."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_demo()
        elif sys.argv[1] == "test":
            test_conditional_flow_enhanced()
        else:
            print("Usage: python enhanced_test.py [interactive|test]")
    else:
        # Default: run both
        test_conditional_flow_enhanced()
        print("\n🎯 Want to try interactive mode? Run: python enhanced_test.py interactive")


if __name__ == "__main__":
    main()
