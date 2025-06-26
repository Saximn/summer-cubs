"""
LangGraph-based chatbot with conditional database querying.
"""

from typing import Dict, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

try:
    from database_utils import init_database, create_sql_toolkit, query_as_list, safe_query_as_list
    from vector_utils import (
        init_embeddings, 
        init_vector_store, 
        add_texts_to_vector_store, 
        create_search_tool
    )
    from agent_utils import init_llm, create_agent, get_current_datetime, get_current_date, get_current_time
    from prompts import system_message, description, suffix
except ImportError:
    # Fallback for relative imports
    from .database_utils import init_database, create_sql_toolkit, query_as_list, safe_query_as_list
    from .vector_utils import (
        init_embeddings, 
        init_vector_store, 
        add_texts_to_vector_store, 
        create_search_tool
    )
    from .agent_utils import init_llm, create_agent, get_current_datetime, get_current_date, get_current_time
    from .prompts import system_message, description, suffix


class ChatbotState(TypedDict):
    """State object for the chatbot workflow."""
    messages: list
    user_query: str
    needs_database: bool
    database_result: str
    final_answer: str


class LangGraphChatbot:
    """A LangGraph-based chatbot with conditional database querying."""
    
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
        self._setup_vector_store_optimized()  # Use optimized version
        self._setup_database_agent()
        self._setup_workflow()
    
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
        
        # Populate vector store with skills and specialties using safe functions
        skills = safe_query_as_list(self.db, "skills", "skill")
        specialties = safe_query_as_list(self.db, "doctors", "specialty")
        
        if skills:
            add_texts_to_vector_store(self.vector_store, skills)
        if specialties:
            add_texts_to_vector_store(self.vector_store, specialties)
    
    def _setup_vector_store_optimized(self):
        """Initialize vector store with smart caching to avoid re-embedding."""
        # Initialize embeddings and vector store
        self.embeddings = init_embeddings(self.embedding_model)
        self.vector_store = init_vector_store(
            name="medical_collection",
            embeddings=self.embeddings,
            directory=self.vector_store_dir
        )
        
        # Check if vector store already has data
        try:
            # Try to search for something to see if data exists
            test_results = self.vector_store.similarity_search("cardiology", k=1)
            if test_results:
                print(f"✅ Vector store already populated with {len(test_results)} items. Skipping re-embedding.")
                return
        except Exception:
            print("🔄 Vector store empty or corrupted. Populating with fresh data...")
        
        # Only populate if empty or corrupted
        skills = safe_query_as_list(self.db, "skills", "skill")
        specialties = safe_query_as_list(self.db, "doctors", "specialty")
        
        if skills:
            print(f"📝 Embedding {len(skills)} skills...")
            add_texts_to_vector_store(self.vector_store, skills)
        
        if specialties:
            print(f"📝 Embedding {len(specialties)} specialties...")
            add_texts_to_vector_store(self.vector_store, specialties)
        
        print("✅ Vector store setup complete!")

    def _setup_database_agent(self):
        """Initialize the database agent with tools."""
        # Get SQL tools
        sql_tools = create_sql_toolkit(self.db, self.llm)
        
        # Create retriever tool
        retriever_tool = create_search_tool(
            self.vector_store,
            name="search_proper_nouns",
            description=description
        )
        
        # Create datetime tools
        datetime_tools = [get_current_datetime, get_current_date, get_current_time]
        
        # Combine all tools
        self.tools = sql_tools + [retriever_tool] + datetime_tools
        
        # Create the agent with combined system message
        system_prompt = f"{system_message}\n\n{suffix}"
        self.database_agent = create_agent(self.llm, self.tools, system_prompt)
    
    def _setup_workflow(self):
        """Set up the LangGraph workflow."""
        # Create the workflow graph
        workflow = StateGraph(ChatbotState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("query_database", self._query_database)
        workflow.add_node("general_response", self._general_response)
        workflow.add_node("format_response", self._format_response)
        
        # Set entry point
        workflow.set_entry_point("analyze_query")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self._should_use_database,
            {
                "database": "query_database",
                "general": "general_response"
            }
        )
        
        # Add edges to format response
        workflow.add_edge("query_database", "format_response")
        workflow.add_edge("general_response", "format_response")
        workflow.add_edge("format_response", END)
        
        # Compile the workflow
        self.workflow = workflow.compile()
    
    def _analyze_query(self, state: ChatbotState) -> ChatbotState:
        """Analyze the user query to determine if database access is needed."""
        user_query = state["user_query"]
        
        # Create a prompt to analyze if database is needed
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are an analyzer that determines if a user query requires database access.

Respond with "YES" if the query:
- Asks about specific medical data (doctors, patients, skills, specialties)
- Requests counts, statistics, or specific information
- Mentions medical procedures, conditions, or healthcare data
- Asks "how many", "list", "find", "search" for medical information
- Asks about current time, date, or datetime information
- Needs to schedule appointments or time-related queries

Respond with "NO" if the query:
- Is a general greeting or conversation
- Asks for definitions or explanations
- Is about general medical knowledge (not specific data)
- Is a casual question not requiring database lookup

Query: {query}

Answer with only YES or NO.
"""),
            ("user", "{query}")
        ])
        
        # Get the analysis
        analysis_chain = analysis_prompt | self.llm
        result = analysis_chain.invoke({"query": user_query})
        
        # Determine if database is needed
        needs_database = "YES" in result.content.upper()
        
        state["needs_database"] = needs_database
        print(f"Query analysis: {'Database needed' if needs_database else 'General response'}")
        
        return state
    
    def _should_use_database(self, state: ChatbotState) -> Literal["database", "general"]:
        """Conditional edge function to route based on analysis."""
        return "database" if state["needs_database"] else "general"
    
    def _query_database(self, state: ChatbotState) -> ChatbotState:
        """Query the database using the agent with recursion limit handling."""
        user_query = state["user_query"]
        print("Querying database...")
        
        try:
            # Use the database agent to get response with recursion limit
            response_messages = []
            config = {"recursion_limit": 10}  # Limit recursion to prevent infinite loops
            
            for step in self.database_agent.stream(
                {"messages": [{"role": "user", "content": user_query}]},
                config=config,
                stream_mode="values",
            ):
                response_messages = step["messages"]
            
            # Get the final response
            if response_messages:
                database_result = response_messages[-1].content
            else:
                database_result = "I couldn't retrieve information from the database."
                
        except Exception as e:
            print(f"Error querying database: {e}")
            # Fallback: try a simple direct query approach
            database_result = self._fallback_database_query(user_query)
        
        state["database_result"] = database_result
        return state
    
    def _fallback_database_query(self, query: str) -> str:
        """Fallback method for simple database queries when agent fails."""
        try:
            # Simple pattern matching for common queries
            query_lower = query.lower()
            
            if "how many" in query_lower and "cardiolog" in query_lower:
                result = self.db.run("SELECT COUNT(*) FROM doctors WHERE specialty = 'cardiology'")
                count = result.strip("[](),")
                return f"There are {count} doctors who specialize in cardiology."
            
            elif "how many doctors" in query_lower:
                result = self.db.run("SELECT COUNT(*) FROM doctors")
                count = result.strip("[](),")
                return f"There are {count} doctors in total."
                
            elif "specialties" in query_lower or "list" in query_lower:
                result = self.db.run("SELECT DISTINCT specialty FROM doctors")
                return f"Available specialties: {result}"
                
            else:
                return "I need more specific information to query the database. Please ask about doctor counts, specialties, or specific medical information."
                
        except Exception as e:
            return f"I'm having trouble accessing the database right now. Error: {str(e)}"
    
    def _general_response(self, state: ChatbotState) -> ChatbotState:
        """Provide a general response without database access."""
        user_query = state["user_query"]
        print("Providing general response...")
        
        # Create a general conversation prompt
        general_prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are a helpful medical assistant. Provide helpful, accurate general information.
You do not have access to specific patient or doctor databases.
Be conversational and helpful, but clarify when specific data would require database access.
"""),
            ("user", "{query}")
        ])
        
        # Get general response
        general_chain = general_prompt | self.llm
        result = general_chain.invoke({"query": user_query})
        
        state["database_result"] = result.content
        return state
    
    def _format_response(self, state: ChatbotState) -> ChatbotState:
        """Format the final response."""
        state["final_answer"] = state["database_result"]
        return state
    
    def ask(self, question: str) -> str:
        """Ask a question to the chatbot and get a response."""
        initial_state = ChatbotState(
            messages=[],
            user_query=question,
            needs_database=False,
            database_result="",
            final_answer=""
        )
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state["final_answer"]
    
    def chat_interactive(self):
        """Start an interactive chat session."""
        print("LangGraph Medical Chatbot ready! Type 'quit' to exit.")
        print("I'll automatically determine if I need to check the database or can answer generally.")
        
        while True:
            question = input("\nYou: ")
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            print("\nBot:", self.ask(question))


# Example usage
if __name__ == "__main__":
    # Create chatbot
    bot = LangGraphChatbot()
    
    # Test different types of queries
    test_queries = [
        "Hello, how are you?",
        "How many doctors specialize in cardiology?",
        "What is hypertension?",
        "What time is it now?",
        "What's the current date?",
        "List all available specialties",
        "Thanks for your help!"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"Response: {bot.ask(query)}")
    
    # Uncomment for interactive mode
    # bot.chat_interactive()
