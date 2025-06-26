"""
Test script for the datetime tools in the chatbot.
"""

from agent_utils import get_current_datetime, get_current_date, get_current_time


def test_datetime_tools():
    """Test all datetime tools individually."""
    print("Testing datetime tools:")
    print("-" * 40)
    
    # Test current datetime
    print(f"Current datetime: {get_current_datetime.invoke({})}")
    
    # Test current date
    print(f"Current date: {get_current_date.invoke({})}")
    
    # Test current time
    print(f"Current time: {get_current_time.invoke({})}")


if __name__ == "__main__":
    test_datetime_tools()
