"""Database utility functions for the chatbot."""

import ast
import re
import os
from pathlib import Path
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit


def find_database_path(db_name="doctors.db"):
    """Find the database file by searching up the directory tree."""
    current_dir = Path.cwd()
    
    # First check current directory
    db_path = current_dir / db_name
    if db_path.exists():
        return str(db_path)
    
    # Search up the directory tree
    for parent in current_dir.parents:
        db_path = parent / db_name
        if db_path.exists():
            print(f"Found database at: {db_path}")
            return str(db_path)
    
    # If not found, return the original name (will create new DB)
    print(f"Database '{db_name}' not found. Will create new database.")
    return db_name


def query_as_list(db, query):
    """Execute a database query and return results as a cleaned list."""
    try:
        res = db.run(query)
        if not res or res.strip() == "[]":
            return []
        res = [el for sub in ast.literal_eval(res) for el in sub if el]
        res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
        return list(set(res))
    except Exception as e:
        print(f"Error executing query '{query}': {e}")
        return []


def init_database(db_path):
    """Initialize and return a SQLDatabase instance."""
    # Auto-find database if just filename is provided
    if not os.path.exists(db_path) and os.path.basename(db_path) == db_path:
        db_path = find_database_path(db_path)
    
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def create_sql_toolkit(db, llm):
    """Create and return SQL database toolkit with tools."""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return toolkit.get_tools()


def check_table_exists(db, table_name):
    """Check if a table exists in the database."""
    try:
        # Try to query the table with LIMIT 1
        query = f"SELECT * FROM {table_name} LIMIT 1"
        db.run(query)
        return True
    except Exception:
        return False


def get_available_tables(db):
    """Get list of available tables in the database."""
    try:
        return db.get_usable_table_names()
    except Exception as e:
        print(f"Error getting table names: {e}")
        return []


def safe_query_as_list(db, table_name, column_name):
    """Safely query a table column and return as list, with error handling."""
    if not check_table_exists(db, table_name):
        print(f"Table '{table_name}' does not exist in database")
        return []
    
    query = f"SELECT {column_name} FROM {table_name}"
    return query_as_list(db, query)
