"""
Main entry point for the medical chatbot.
This file demonstrates how to use the modularized chatbot components.
"""

from chatbot import MedicalChatbot


def main():
    """Main function to run the chatbot."""
    # Initialize the chatbot (database path will be auto-discovered)
    bot = MedicalChatbot(
        db_path="doctors.db",  # Will auto-find the database
        model_name="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
        vector_store_dir="./chroma_langchain_db"
    )
    
    # Example question
    question = "How many doctors specialize in cardiology?"
    
    print(f"Question: {question}")
    print("Answer:")
    bot.ask(question)
    
    # Show available skills and specialties
    print("\nAvailable skills:", bot.get_available_skills()[:5])  # Show first 5
    print("Available specialties:", bot.get_available_specialties()[:5])  # Show first 5


if __name__ == "__main__":
    main()