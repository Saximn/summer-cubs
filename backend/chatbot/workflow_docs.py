"""
LangGraph Workflow Visualization and Documentation
"""

# ASCII Flow Diagram
WORKFLOW_DIAGRAM = """
LangGraph Chatbot Conditional Flow:

┌─────────────────┐
│   User Query    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Analyze Query  │  ◄── Determines if database is needed
└─────────┬───────┘
          │
          ▼
    ┌─── ? ───┐
    │ Decision │
    └─── ┬ ───┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────────┐
│Database│  │  General   │
│ Query  │  │ Response   │
└───┬────┘  └─────┬──────┘
    │             │
    └─────┬───────┘
          ▼
┌─────────────────┐
│ Format Response │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Final Answer    │
└─────────────────┘
"""

# Node Descriptions
NODE_DESCRIPTIONS = {
    "analyze_query": """
    Analyzes the user's query using an LLM to determine if it requires database access.
    
    Criteria for database access:
    - Questions about specific medical data
    - Requests for counts or statistics  
    - Mentions of doctors, patients, skills, specialties
    - Search/list/find queries for medical information
    
    Returns: needs_database (bool)
    """,
    
    "query_database": """
    Uses the existing database agent with SQL tools and vector search.
    
    Components:
    - SQL Database toolkit for structured queries
    - Vector store for semantic search of skills/specialties
    - LangChain agent for intelligent query execution
    
    Returns: database_result (str)
    """,
    
    "general_response": """
    Provides conversational responses without database access.
    
    Use cases:
    - Greetings and casual conversation
    - General medical knowledge questions
    - Definitions and explanations
    - Thank you messages
    
    Returns: general_result (str)
    """,
    
    "format_response": """
    Final formatting step before returning to user.
    
    Could be extended to:
    - Add citations for database queries
    - Format medical data in tables
    - Add disclaimers for general responses
    
    Returns: final_answer (str)
    """
}

# Usage Examples
USAGE_EXAMPLES = {
    "Database Queries": [
        "How many cardiologists do we have?",
        "List all doctors with surgery skills",
        "Find patients with diabetes",
        "What specialties are available?",
        "Count all emergency medicine doctors"
    ],
    
    "General Queries": [
        "Hello, how are you?",
        "What is hypertension?",
        "Explain how vaccines work",
        "Thank you for your help",
        "What are the symptoms of flu?"
    ]
}

def print_workflow_info():
    """Print comprehensive workflow information."""
    print("="*60)
    print("LANGGRAPH MEDICAL CHATBOT WORKFLOW")
    print("="*60)
    
    print("\nWORKFLOW DIAGRAM:")
    print(WORKFLOW_DIAGRAM)
    
    print("\nNODE DESCRIPTIONS:")
    print("-" * 40)
    for node, description in NODE_DESCRIPTIONS.items():
        print(f"\n{node.upper().replace('_', ' ')}:")
        print(description)
    
    print("\nUSAGE EXAMPLES:")
    print("-" * 40)
    for category, examples in USAGE_EXAMPLES.items():
        print(f"\n{category}:")
        for example in examples:
            print(f"  • {example}")

if __name__ == "__main__":
    print_workflow_info()
