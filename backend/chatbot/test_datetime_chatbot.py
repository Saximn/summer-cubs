"""
Test the chatbot with datetime queries.
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_chatbot import LangGraphChatbot


def test_chatbot_with_datetime():
    """Test the chatbot with datetime-related queries."""
    print("Testing chatbot with datetime functionality...")
    print("=" * 60)
    
    try:
        # Create chatbot instance
        bot = LangGraphChatbot()
        
        # Test datetime queries
        datetime_queries = [
            "What time is it?",
            "What's the current date?", 
            "Can you tell me the current date and time?",
            "What day is today?"
        ]
        
        for query in datetime_queries:
            print(f"\nQuery: {query}")
            print(f"Response: {bot.ask(query)}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error testing chatbot: {e}")
        print("Make sure you have the required dependencies and database setup.")


if __name__ == "__main__":
    test_chatbot_with_datetime()
