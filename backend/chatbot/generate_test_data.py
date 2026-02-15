"""
Generate realistic test queries and ground truth answers for chatbot evaluation.
"""

import json
import random
from pathlib import Path

try:
    from database_utils import init_database, query_as_list, safe_query_as_list
except ImportError:
    from .database_utils import init_database, query_as_list, safe_query_as_list


def generate_test_dataset(db_path="doctors.db", output_file="evaluation_dataset.json"):
    """Generate comprehensive test dataset with diverse query types."""
    
    db = init_database(db_path)
    test_queries = []
    
    # Get actual data from database for ground truth
    try:
        total_doctors = int(db.run("SELECT COUNT(*) FROM doctors").strip("[](),"))
        specialties = db.run("SELECT DISTINCT specialty FROM doctors")
        all_skills = safe_query_as_list(db, "skills", "skill")
        
        # Parse specialties
        import ast
        specialty_list = []
        if specialties and specialties != "[]":
            specialty_tuples = ast.literal_eval(specialties)
            specialty_list = [s[0] for s in specialty_tuples if s and s[0]]
        
        print(f"Database stats: {total_doctors} doctors, {len(specialty_list)} specialties, {len(all_skills)} unique skills")
        
    except Exception as e:
        print(f"Error querying database: {e}")
        return []
    
    # 1. SIMPLE COUNT QUERIES
    test_queries.append({
        "query": "How many doctors do we have?",
        "relevant_docs": [],
        "expected_route": "database",
        "ground_truth_answer": f"There are {total_doctors} doctors in total.",
        "query_type": "count",
        "sql_pattern": "SELECT COUNT(*) FROM doctors"
    })
    
    test_queries.append({
        "query": "What is the total number of doctors?",
        "relevant_docs": [],
        "expected_route": "database",
        "ground_truth_answer": f"{total_doctors} doctors",
        "query_type": "count",
        "sql_pattern": "SELECT COUNT(*) FROM doctors"
    })
    
    # 2. SPECIALTY QUERIES - More variations
    for specialty in specialty_list:  # All specialties
        try:
            count = db.run(f"SELECT COUNT(*) FROM doctors WHERE specialty = '{specialty}'")
            count_val = int(count.strip("[](),"))
            
            # Multiple query variations for each specialty
            specialty_queries = [
                f"How many doctors specialize in {specialty}?",
                f"List all {specialty} doctors",
                f"Find {specialty} specialists",
                f"Show me doctors in {specialty}",
                f"Count of {specialty} doctors"
            ]
            
            for idx, sq in enumerate(specialty_queries):
                test_queries.append({
                    "query": sq,
                    "relevant_docs": [specialty],
                    "expected_route": "database",
                    "ground_truth_answer": f"There are {count_val} doctors who specialize in {specialty}." if "how many" in sq.lower() or "count" in sq.lower() else f"Doctors specializing in {specialty}",
                    "query_type": "specialty_count" if "how many" in sq.lower() or "count" in sq.lower() else "specialty_list",
                    "sql_pattern": f"SELECT COUNT(*) FROM doctors WHERE specialty = '{specialty}'" if "how many" in sq.lower() or "count" in sq.lower() else f"SELECT * FROM doctors WHERE specialty = '{specialty}'"
                })
        except Exception as e:
            print(f"Error processing specialty {specialty}: {e}")
    
    # 3. SKILL-BASED QUERIES - More variations
    sample_skills = random.sample(all_skills, min(20, len(all_skills)))
    for skill in sample_skills:
        skill_variations = [
            f"Find doctors with {skill} skills",
            f"Who has {skill} expertise?",
            f"List doctors skilled in {skill}",
            f"Show me {skill} specialists"
        ]
        for sv in skill_variations[:2]:  # 2 variations per skill
            test_queries.append({
                "query": sv,
                "relevant_docs": [skill],
                "expected_route": "database",
                "ground_truth_answer": f"Doctors with {skill} skill",
                "query_type": "skill_search",
                "sql_pattern": f"SELECT * FROM doctors WHERE id IN (SELECT doctor_id FROM skills WHERE skill = '{skill}')"
            })
    
    # 4. COMPLEX QUERIES
    if len(specialty_list) >= 2:
        spec1, spec2 = specialty_list[0], specialty_list[1]
        test_queries.append({
            "query": f"How many doctors work on Monday and specialize in {spec1}?",
            "relevant_docs": [spec1],
            "expected_route": "database",
            "ground_truth_answer": f"Doctors working Monday with {spec1} specialty",
            "query_type": "complex_join",
            "sql_pattern": "JOIN with schedule table"
        })
        
        test_queries.append({
            "query": f"Compare the number of {spec1} vs {spec2} doctors",
            "relevant_docs": [spec1, spec2],
            "expected_route": "database",
            "ground_truth_answer": "Comparison of specialty counts",
            "query_type": "comparison",
            "sql_pattern": "Multiple SELECT COUNT queries"
        })
    
    # 5. GENERAL MEDICAL QUESTIONS (no database)
    general_queries = [
        {
            "query": "What is hypertension?",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "Hypertension is high blood pressure, a condition where the force of blood against artery walls is too high.",
            "query_type": "general_definition",
            "sql_pattern": None
        },
        {
            "query": "What are the symptoms of diabetes?",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "Common diabetes symptoms include increased thirst, frequent urination, extreme fatigue, and blurred vision.",
            "query_type": "general_symptoms",
            "sql_pattern": None
        },
        {
            "query": "How does the heart work?",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "The heart pumps blood through a network of arteries and veins, delivering oxygen and nutrients to the body.",
            "query_type": "general_anatomy",
            "sql_pattern": None
        },
        {
            "query": "What is a CT scan used for?",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "CT scans create detailed cross-sectional images of the body to help diagnose diseases and injuries.",
            "query_type": "general_procedure",
            "sql_pattern": None
        }
    ]
    test_queries.extend(general_queries)
    
    # 6. DATETIME QUERIES
    datetime_queries = [
        {
            "query": "What time is it?",
            "relevant_docs": [],
            "expected_route": "database",
            "ground_truth_answer": "Current time from system",
            "query_type": "datetime_time",
            "sql_pattern": None,
            "requires_tool": "get_current_time"
        },
        {
            "query": "What is today's date?",
            "relevant_docs": [],
            "expected_route": "database",
            "ground_truth_answer": "Current date from system",
            "query_type": "datetime_date",
            "sql_pattern": None,
            "requires_tool": "get_current_date"
        },
        {
            "query": "What is the current date and time?",
            "relevant_docs": [],
            "expected_route": "database",
            "ground_truth_answer": "Current datetime from system",
            "query_type": "datetime_full",
            "sql_pattern": None,
            "requires_tool": "get_current_datetime"
        }
    ]
    test_queries.extend(datetime_queries)
    
    # 7. GREETING/CASUAL QUERIES (no database)
    casual_queries = [
        {
            "query": "Hello, how are you?",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "Greeting response",
            "query_type": "greeting",
            "sql_pattern": None
        },
        {
            "query": "Thanks for your help!",
            "relevant_docs": [],
            "expected_route": "general",
            "ground_truth_answer": "Acknowledgment response",
            "query_type": "acknowledgment",
            "sql_pattern": None
        }
    ]
    test_queries.extend(casual_queries)
    
    # 8. EDGE CASES
    edge_cases = [
        {
            "query": "Show me all doctors",
            "relevant_docs": [],
            "expected_route": "database",
            "ground_truth_answer": f"List of all {total_doctors} doctors",
            "query_type": "list_all",
            "sql_pattern": "SELECT * FROM doctors"
        },
        {
            "query": "What specialties are available?",
            "relevant_docs": specialty_list,
            "expected_route": "database",
            "ground_truth_answer": f"Available specialties: {', '.join(specialty_list[:5])}...",
            "query_type": "list_specialties",
            "sql_pattern": "SELECT DISTINCT specialty FROM doctors"
        }
    ]
    test_queries.extend(edge_cases)
    
    # Add metadata
    dataset = {
        "metadata": {
            "total_queries": len(test_queries),
            "database_queries": len([q for q in test_queries if q["expected_route"] == "database"]),
            "general_queries": len([q for q in test_queries if q["expected_route"] == "general"]),
            "query_types": list(set([q["query_type"] for q in test_queries])),
            "database_stats": {
                "total_doctors": total_doctors,
                "specialties": specialty_list,
                "unique_skills": len(all_skills)
            }
        },
        "queries": test_queries
    }
    
    # Save to JSON
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"\n✅ Generated {len(test_queries)} test queries")
    print(f"   - Database queries: {dataset['metadata']['database_queries']}")
    print(f"   - General queries: {dataset['metadata']['general_queries']}")
    print(f"   - Query types: {len(dataset['metadata']['query_types'])}")
    print(f"   - Saved to: {output_path}")
    
    return test_queries


if __name__ == "__main__":
    # Generate test dataset
    queries = generate_test_dataset()
    
    if queries:
        print("\nSample queries:")
        for i, query in enumerate(queries[:5]):
            print(f"{i+1}. [{query['query_type']}] {query['query']}")
