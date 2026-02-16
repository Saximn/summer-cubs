#!/usr/bin/env python
"""Check database and generate aligned evaluation dataset."""

import json
try:
    from chatbot.database_utils import init_database, safe_query_as_list
except ImportError:
    from database_utils import init_database, safe_query_as_list

# Check database
db = init_database('doctors.db')
skills = safe_query_as_list(db, 'skills', 'skill')
specialties = safe_query_as_list(db, 'doctors', 'specialty')

print('=== DATABASE CONTENTS ===')
print(f'Specialties ({len(set(specialties))}): {sorted(set(specialties))}')
print(f'\nUnique skills ({len(set(skills))}): {sorted(set(skills))}')

# Check evaluation dataset
try:
    dataset_path = 'evaluation_dataset.json'
    with open(dataset_path) as f:
        data = json.load(f)
except:
    dataset_path = '../evaluation_dataset.json'  
    with open(dataset_path) as f:
        data = json.load(f)
    print(f'\n=== EVALUATION DATASET ===')
    print(f'Total queries: {len(data["queries"])}')
    print(f'\nFirst 10 queries with expected routes:')
    for i, q in enumerate(data['queries'][:10]):
        route = q.get("expected_route", "N/A")
        print(f'{i+1}. "{q["query"]}" → {route}')

print("\n=== ALIGNMENT MAPPING ===")
print("Database specialties should map to:")
spec_map = {
    "cardiology": ["cardiology", "cardiac", "heart", "cardiologist"],
    "neurology": ["neurology", "neurological", "brain", "neurologist"],
    "gastroenterology": ["gastroenterology", "GI", "stomach", "gastro"],
    "dermatology": ["dermatology", "skin", "dermatologist"],
    "orthopedics": ["orthopedics", "bone", "joint", "orthopedist"],
    "pediatrics": ["pediatrics", "child", "children", "pediatrician"],
    "endocrinology": ["endocrinology", "hormone", "thyroid", "endocrinologist"],
    "urology": ["urology", "urological", "kidney", "urologist"],
    "psychiatry": ["psychiatry", "psychiatric", "mental", "psychiatrist"],
    "oncology": ["oncology", "cancer", "tumor", "oncologist"],
}
for spec, aliases in spec_map.items():
    print(f"  {spec}: {', '.join(aliases[1:])}")
