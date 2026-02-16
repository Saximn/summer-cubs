#!/usr/bin/env python3
"""Audit the evaluation dataset expectations."""

import json
from pathlib import Path

dataset_path = Path(__file__).parent / "evaluation_dataset_aligned.json"
with open(dataset_path, 'r') as f:
    dataset = json.load(f)

print("="*70)
print("EVALUATION DATASET AUDIT")
print("="*70)

# Load database to see what's really there
import sqlite3
db_path = Path(__file__).parent / "doctors.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
db_specialties = set(row[0] for row in cursor.fetchall())
cursor.execute("SELECT skill FROM skills")
db_skills = set(row[0] for row in cursor.fetchall())

conn.close()

print(f"\nDatabase has {len(db_specialties)} specialties and {len(db_skills)} skills")
print(f"Specialties: {sorted(db_specialties)}")
print()

# Check dataset expectations
all_expected = set()
mismatches = []

for i, query_obj in enumerate(dataset['queries'][:5]):
    query = query_obj['query']
    expected = set(query_obj.get('relevance_grades', {}).keys())
    all_expected.update(expected)
    
    # Check if expected docs are in database
    in_db = expected & (db_specialties | db_skills)
    not_in_db = expected - (db_specialties | db_skills)
    
    if not_in_db:
        mismatches.append({
            'query': query,
            'expected': expected,
            'in_db': in_db,
            'missing': not_in_db
        })

print(f"Sample queries (first 5):")
for mm in mismatches:
    print(f"\n  Query: {mm['query']}")
    print(f"    Expected: {mm['expected']}")
    print(f"    In DB: {mm['in_db']}")
    print(f"    NOT in DB: {mm['missing']}")
