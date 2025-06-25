"""
Alternative entry point - Interactive chatbot session
"""

from chatbot import MedicalChatbot


def interactive_session():
    """Run an interactive chatbot session."""
    print("Initializing Medical Chatbot...")
    bot = MedicalChatbot()
    
    print("Medical Chatbot ready! Type 'quit' to exit.")
    
    while True:
        question = input("\nAsk a question: ")
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        print("\nAnswer:")
        bot.ask(question)


if __name__ == "__main__":
    interactive_session()
