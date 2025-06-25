"""
Medical Chatbot Package

A modular chatbot system for querying medical databases with semantic search capabilities.
"""

from .chatbot import MedicalChatbot
from .database_utils import init_database, query_as_list, create_sql_toolkit
from .vector_utils import init_embeddings, init_vector_store, create_search_tool
from .agent_utils import init_llm, create_agent, answer_question

__all__ = [
    'MedicalChatbot',
    'init_database',
    'query_as_list', 
    'create_sql_toolkit',
    'init_embeddings',
    'init_vector_store',
    'create_search_tool',
    'init_llm',
    'create_agent',
    'answer_question'
]

__version__ = "1.0.0"
