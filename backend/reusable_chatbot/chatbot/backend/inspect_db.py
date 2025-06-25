"""
Database inspection script to understand the structure of doctors.db
"""

from database_utils import init_database, query_as_list, get_available_tables


def inspect_database(db_path="doctors.db"):
    """Inspect the database structure and contents."""
    print(f"Inspecting database: {db_path}")
    print("=" * 50)
    
    try:
        db = init_database(db_path)
        
        # Get available tables
        tables = get_available_tables(db)
        print(f"Available tables: {tables}")
        
        if not tables:
            print("No tables found in database!")
            return
        
        # Inspect each table
        for table in tables:
            print(f"\n--- Table: {table} ---")
            
            try:
                # Get table schema
                schema_query = f"PRAGMA table_info({table})"
                schema_result = db.run(schema_query)
                print(f"Schema: {schema_result}")
                
                # Get row count
                count_query = f"SELECT COUNT(*) FROM {table}"
                count_result = db.run(count_query)
                print(f"Row count: {count_result}")
                
                # Get sample data
                sample_query = f"SELECT * FROM {table} LIMIT 5"
                sample_result = db.run(sample_query)
                print(f"Sample data: {sample_result}")
                
            except Exception as e:
                print(f"Error inspecting table {table}: {e}")
        
        print("\n" + "=" * 50)
        print("RECOMMENDATIONS:")
        
        # Check for expected tables and suggest alternatives
        if "skills" not in tables:
            print("❌ 'skills' table not found")
            # Look for similar tables
            skill_tables = [t for t in tables if 'skill' in t.lower()]
            if skill_tables:
                print(f"   Found similar tables: {skill_tables}")
            else:
                print("   No skill-related tables found")
        
        if "doctors" not in tables:
            print("❌ 'doctors' table not found")
            # Look for similar tables
            doctor_tables = [t for t in tables if 'doctor' in t.lower() or 'physician' in t.lower()]
            if doctor_tables:
                print(f"   Found similar tables: {doctor_tables}")
            else:
                print("   No doctor-related tables found")
        
        # Suggest how to proceed
        print("\nSUGGESTED FIXES:")
        print("1. Update the chatbot to use the actual table names found above")
        print("2. Or create the expected tables (skills, doctors) with proper schema")
        print("3. Or modify the vector store setup to skip missing tables")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("\nPossible issues:")
        print("- Database file doesn't exist")
        print("- Database file is corrupted")
        print("- Wrong database path")


if __name__ == "__main__":
    inspect_database()
