"""
Test script for the LangGraph chatbot workflow.
"""

from langgraph_chatbot import LangGraphChatbot


def test_conditional_flow():
    """Test the conditional flow of the chatbot."""
    print("Initializing LangGraph Chatbot...")
    bot = LangGraphChatbot()
    
    # Test cases that should NOT use database
    general_queries = [
        "Hello, how are you today?",
        "What is the definition of hypertension?",
        "Can you explain what diabetes is?",
        "Thank you for your help",
        "How does the heart work?"
    ]
    
    # Test cases that SHOULD use database
    database_queries = [
        "How many doctors do we have?",
        "List all cardiologists",
        "How many patients have diabetes?",
        "Find doctors with surgery skills",
        "What specialties are available?",
        "Count all doctors in cardiology"
    ]
    
    print("\n" + "="*60)
    print("TESTING GENERAL QUERIES (should NOT use database)")
    print("="*60)
    
    for query in general_queries:
        print(f"\nQuery: {query}")
        print("Response:", bot.ask(query))
        print("-" * 40)
    
    print("\n" + "="*60)
    print("TESTING DATABASE QUERIES (should use database)")
    print("="*60)
    
    for query in database_queries:
        print(f"\nQuery: {query}")
        print("Response:", bot.ask(query))
        print("-" * 40)


def interactive_mode():
    """Run interactive chatbot session."""
    bot = LangGraphChatbot()
    bot.chat_interactive()


if __name__ == "__main__":
    # Choose what to run
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        test_conditional_flow()
