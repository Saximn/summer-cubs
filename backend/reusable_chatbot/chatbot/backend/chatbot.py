"""Main chatbot class that orchestrates all components."""

import os
from typing import List

from prompts import system_message, description, suffix
from database_utils import init_database, create_sql_toolkit, query_as_list, safe_query_as_list, get_available_tables
from vector_utils import (
    init_embeddings, 
    init_vector_store, 
    add_texts_to_vector_store, 
    create_search_tool
)
from agent_utils import init_llm, create_agent, answer_question


class MedicalChatbot:
    """A chatbot for querying medical database with semantic search capabilities."""
    
    def __init__(
        self, 
        db_path: str = "doctors.db",
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        vector_store_dir: str = "./chroma_langchain_db"
    ):
        """Initialize the chatbot with database and AI models."""
        self.db_path = db_path
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.vector_store_dir = vector_store_dir
        
        # Initialize components
        self._setup_database()
        self._setup_llm()
        self._setup_vector_store()
        self._setup_agent()
    
    def _setup_database(self):
        """Initialize database connection and tools."""
        self.db = init_database(self.db_path)
        
    def _setup_llm(self):
        """Initialize the language model."""
        self.llm = init_llm(self.model_name, "openai")
        
    def _setup_vector_store(self):
        """Initialize vector store and populate with data."""
        # Initialize embeddings and vector store
        self.embeddings = init_embeddings(self.embedding_model)
        self.vector_store = init_vector_store(
            name="medical_collection",
            embeddings=self.embeddings,
            directory=self.vector_store_dir
        )
        
        # Check what tables are available
        available_tables = get_available_tables(self.db)
        print(f"Available tables in database: {available_tables}")
        
        # Safely populate vector store with available data
        skills = safe_query_as_list(self.db, "skills", "skill")
        specialties = safe_query_as_list(self.db, "doctors", "specialty")
        
        # If no skills/specialties tables, try alternative approaches
        if not skills and not specialties:
            print("No skills or specialties tables found. Checking for alternative data...")
            # Try some common table/column combinations
            for table in available_tables:
                print(f"Checking table: {table}")
                try:
                    # Get a sample of data to see what's available
                    sample_data = query_as_list(self.db, f"SELECT * FROM {table} LIMIT 3")
                    if sample_data:
                        print(f"Sample data from {table}: {sample_data[:3]}")
                except Exception as e:
                    print(f"Error sampling {table}: {e}")
        
        if skills:
            print(f"Adding {len(skills)} skills to vector store")
            add_texts_to_vector_store(self.vector_store, skills)
        
        if specialties:
            print(f"Adding {len(specialties)} specialties to vector store")
            add_texts_to_vector_store(self.vector_store, specialties)
        
    def _setup_agent(self):
        """Initialize the agent with tools."""
        # Get SQL tools
        sql_tools = create_sql_toolkit(self.db, self.llm)
        
        # Create retriever tool
        retriever_tool = create_search_tool(
            self.vector_store,
            name="search_proper_nouns",
            description=description
        )
        
        # Combine all tools
        self.tools = sql_tools + [retriever_tool]
        
        # Create the agent with combined system message
        system_prompt = f"{system_message}\n\n{suffix}"
        self.agent = create_agent(self.llm, self.tools, system_prompt)
    
    def ask(self, question: str):
        """Ask a question to the chatbot."""
        answer_question(self.agent, question)
    
    def get_available_skills(self) -> List[str]:
        """Get list of available skills from the database."""
        return safe_query_as_list(self.db, "skills", "skill")
    
    def get_available_specialties(self) -> List[str]:
        """Get list of available specialties from the database."""
        return safe_query_as_list(self.db, "doctors", "specialty")
