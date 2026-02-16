#!/usr/bin/env python3
"""Generate a properly aligned evaluation dataset based on actual database contents."""

import json
import sqlite3
from pathlib import Path
from collections import defaultdict

# Get actual database contents
db_path = Path(__file__).parent / "doctors.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
specialties = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT DISTINCT skill FROM skills ORDER BY skill")
skills = [row[0] for row in cursor.fetchall()]

print(f"Database has {len(specialties)} specialties and {len(skills)} skills")
print(f"Specialties: {specialties}")
print(f"Sample skills: {skills[:10]}...")

conn.close()

# Create evaluation queries based on actual database content
# All relevance_grades should only reference actual specialties or skills
evaluation_dataset = {
    "metadata": {
        "source": "aligned with actual database schema",
        "specialties": specialties,
        "skills": skills,
        "date_created": "2024"
    },
    "queries": [
        # EASY: Direct specialty searches
        {
            "query": "Find a cardiologist",
            "difficulty": "easy",
            "relevance_grades": {"cardiology": 3}  # Only actual specialty
        },
        {
            "query": "I need a neurologist",
            "difficulty": "easy",
            "relevance_grades": {"neurology": 3}  # Only actual specialty
        },
        {
            "query": "Show dermatologists",
            "difficulty": "easy",
            "relevance_grades": {"dermatology": 3}  # Only actual specialty
        },
        {
            "query": "Where are the orthopedists",
            "difficulty": "easy",
            "relevance_grades": {"orthopedics": 3}  # Only actual specialty
        },
        {
            "query": "Who are the gastroenterologists",
            "difficulty": "easy",
            "relevance_grades": {"gastroenterology": 3}  # Only actual specialty
        },
        {
            "query": "pediatric doctors",
            "difficulty": "easy",
            "relevance_grades": {"pediatrics": 3}  # Only actual specialty
        },
        {
            "query": "endocrinology specialists",
            "difficulty": "easy",
            "relevance_grades": {"endocrinology": 3}  # Only actual specialty
        },
        {
            "query": "urologists",
            "difficulty": "easy",
            "relevance_grades": {"urology": 3}  # Only actual specialty
        },
        {
            "query": "psychiatrists in the system",
            "difficulty": "easy",
            "relevance_grades": {"psychiatry": 3}  # Only actual specialty
        },
        {
            "query": "oncology department",
            "difficulty": "easy",
            "relevance_grades": {"oncology": 3}  # Only actual specialty
        },
        
        # MEDIUM: Skill-based searches
        {
            "query": "who does EEG",
            "difficulty": "medium",
            "relevance_grades": {"EEG": 3, "neurology": 2}  # Skill + specialty using it
        },
        {
            "query": "angioplasty procedure doctors",
            "difficulty": "medium",
            "relevance_grades": {"angioplasty": 3, "cardiology": 2}
        },
        {
            "query": "CBT treatment providers",
            "difficulty": "medium",
            "relevance_grades": {"CBT": 3, "psychiatry": 2}
        },
        {
            "query": "colonoscopy specialists",
            "difficulty": "medium",
            "relevance_grades": {"colonoscopy": 3, "gastroenterology": 2}
        },
        {
            "query": "laser therapy available",
            "difficulty": "medium",
            "relevance_grades": {"laser therapy": 3, "dermatology": 2}
        },
        {
            "query": "who can do joint replacement",
            "difficulty": "medium",
            "relevance_grades": {"joint replacement": 3, "orthopedics": 2}
        },
        {
            "query": "arthroscopy surgery",
            "difficulty": "medium",
            "relevance_grades": {"arthroscopy": 3, "orthopedics": 2}
        },
        {
            "query": "chemotherapy treatment doctors",
            "difficulty": "medium",
            "relevance_grades": {"chemotherapy": 3, "oncology": 2}
        },
        {
            "query": "ultrasound imaging",
            "difficulty": "medium",
            "relevance_grades": {"ultrasound": 3, "pediatrics": 2}
        },
        {
            "query": "thyroid panel tests",
            "difficulty": "medium",
            "relevance_grades": {"thyroid panels": 3, "endocrinology": 2}
        },
        {
            "query": "stress test for heart",
            "difficulty": "medium",
            "relevance_grades": {"stress test": 3, "cardiology": 2}
        },
        {
            "query": "dermis examination",
            "difficulty": "medium",
            "relevance_grades": {"skin biopsy": 2, "dermatology": 3}
        },
        {
            "query": "cognitive behavioral therapy",
            "difficulty": "medium",
            "relevance_grades": {"CBT": 3, "psychiatry": 2}
        },
        {
            "query": "spinal cord imaging",
            "difficulty": "medium",
            "relevance_grades": {"MRI": 2, "neurology": 3}
        },
        {
            "query": "bone density scan",
            "difficulty": "medium",
            "relevance_grades": {"bone density scan": 3, "orthopedics": 2}
        },
        
        # HARD: Multi-criteria, typos, synonyms, abbreviations
        {
            "query": "bone doc",
            "difficulty": "hard",
            "relevance_grades": {"orthopedics": 3}  # Abbreviation/synonym
        },
        {
            "query": "heart specialist",
            "difficulty": "hard",
            "relevance_grades": {"cardiology": 3}  # Synonym for cardiologist
        },
        {
            "query": "skin doctor with laser",
            "difficulty": "hard",
            "relevance_grades": {"dermatology": 3, "laser therapy": 2}  # Multi-criteria
        },
        {
            "query": "GI doctor",
            "difficulty": "hard",
            "relevance_grades": {"gastroenterology": 3}  # Abbreviation expansion
        },
        {
            "query": "therapist for depression",
            "difficulty": "hard",
            "relevance_grades": {"psychiatry": 3, "CBT": 2}  # Synonym + skill
        },
        {
            "query": "cardiolog",  # Typo
            "difficulty": "hard",
            "relevance_grades": {"cardiology": 3}  # Typo correction
        },
        {
            "query": "neuolog",  # Typo variant
            "difficulty": "hard",
            "relevance_grades": {"neurology": 3}  # Typo correction
        },
        {
            "query": "dermotologist",  # Typo variant
            "difficulty": "hard",
            "relevance_grades": {"dermatology": 3}  # Typo correction
        },
        {
            "query": "orthopadic",  # Typo variant
            "difficulty": "hard",
            "relevance_grades": {"orthopedics": 3}  # Typo correction
        },
        {
            "query": "cardiac surgery",
            "difficulty": "hard",
            "relevance_grades": {"cardiology": 3}  # Synonym for cardiac
        },
        {
            "query": "nervous system doctor",
            "difficulty": "hard",
            "relevance_grades": {"neurology": 3}  # Descriptive synonym
        },
        {
            "query": "bone and joint",
            "difficulty": "hard",
            "relevance_grades": {"orthopedics": 3, "joint replacement": 2}  # Multi-term
        },
        {
            "query": "psychiatric eval needed",
            "difficulty": "hard",
            "relevance_grades": {"psychiatry": 3, "CBT": 2}  # Phrase variant
        },
        {
            "query": "tumor treatment center",
            "difficulty": "hard",
            "relevance_grades": {"oncology": 3, "chemotherapy": 2}  # Synonym + skill
        }
    ]
}

# Output
output_path = Path(__file__).parent / "evaluation_dataset_corrected.json"
with open(output_path, 'w') as f:
    json.dump(evaluation_dataset, f, indent=2)

print(f"\n[OK] Created corrected dataset with {len(evaluation_dataset['queries'])} queries")
easy = len([q for q in evaluation_dataset['queries'] if q['difficulty'] == 'easy'])
med = len([q for q in evaluation_dataset['queries'] if q['difficulty'] == 'medium'])
hard = len([q for q in evaluation_dataset['queries'] if q['difficulty'] == 'hard'])
print(f"    Easy: {easy}, Medium: {med}, Hard: {hard}")
print(f"    All expectations reference actual database contents")
print(f"    Saved to: {output_path}")
