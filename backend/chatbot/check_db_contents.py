#!/usr/bin/env python3
"""Check what specialties and skills are in the database."""

import sqlite3

db_path = "./doctors.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*70)
print("DATABASE CONTENTS")
print("="*70)

# Get specialties
print("\nSPECIALTIES:")
cursor.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
specialties = [row[0] for row in cursor.fetchall()]
print(f"  Total: {len(specialties)}")
for spec in specialties:
    print(f"    - {spec}")

# Get skills
print("\nSKILLS:")
cursor.execute("SELECT skill FROM skills ORDER BY skill")
skills = [row[0] for row in cursor.fetchall()]
print(f"  Total: {len(skills)}")
for skill in skills[:15]:
    print(f"    - {skill}")
print(f"    ... and {len(skills)-15} more")

# Check doctor count
print("\nDOCTORS:")
cursor.execute("SELECT COUNT(*) FROM doctors")
doc_count = cursor.fetchone()[0]
print(f"  Total: {doc_count}")

conn.close()
