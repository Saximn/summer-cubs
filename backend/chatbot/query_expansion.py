"""Query expansion module for medical terminology and synonyms."""

from typing import List, Set
import re


class MedicalQueryExpander:
    """Expands medical queries with synonyms and related terms."""
    
    def __init__(self):
        """Initialize expansion mappings."""
        # Symptom to specialty mappings
        self.symptom_specialty_map = {
            "chest pain": ["cardiology", "cardiac"],
            "heart": ["cardiology", "cardiac"],
            "cardiac": ["cardiology", "heart"],
            "headache": ["neurology", "brain"],
            "brain": ["neurology", "Neural"],
            "neurological": ["neurology", "brain"],
            "stomach pain": ["gastroenterology", "GI", "digestive"],
            "stomach": ["gastroenterology", "GI", "abdominal"],
            "GI": ["gastroenterology", "stomach", "digestive"],
            "digestive": ["gastroenterology", "stomach"],
            "skin": ["dermatology", "epidermis"],
            "dermatological": ["dermatology", "skin"],
            "bone": ["orthopedics", "skeletal"],
            "joint": ["orthopedics", "bone"],
            "skeletal": ["orthopedics", "bone"],
            "cancer": ["oncology", "tumor", "malignant"],
            "tumor": ["oncology", "cancer"],
            "thyroid": ["endocrinology", "hormone"],
            "hormone": ["endocrinology", "thyroid"],
            "mental health": ["psychiatry", "psychiatric"],
            "psychological": ["psychiatry", "mental"],
            "kidney": ["urology", "urological"],
            "urological": ["urology", "kidney"],
            "child": ["pediatrics", "children", "infant"],
            "children": ["pediatrics", "child"],
            "pediatric": ["pediatrics", "child"],
        }
        
        # Procedure to specialty mappings
        self.procedure_specialty_map = {
            "angioplasty": ["cardiology"],
            "echocardiogram": ["cardiology"],
            "stress test": ["cardiology"],
            "EEG": ["neurology"],
            "EMG": ["neurology"],
            "lumbar puncture": ["neurology"],
            "colonoscopy": ["gastroenterology"],
            "upper endoscopy": ["gastroenterology"],
            "liver biopsy": ["gastroenterology"],
            "skin biopsy": ["dermatology"],
            "laser therapy": ["dermatology"],
            "mole removal": ["dermatology"],
            "joint replacement": ["orthopedics"],
            "arthroscopy": ["orthopedics"],
            "fracture fixation": ["orthopedics"],
            "chemotherapy": ["oncology"],
            "radiation planning": ["oncology"],
            "tumor biopsy": ["oncology"],
            "insulin therapy": ["endocrinology"],
            "thyroid panels": ["endocrinology"],
            "bone density scan": ["endocrinology"],
            "psychiatric eval": ["psychiatry"],
            "CBT": ["psychiatry"],
            "medication management": ["psychiatry"],
            "cystoscopy": ["urology"],
            "urinalysis": ["urology"],
            "prostate biopsy": ["urology"],
            "well-child exam": ["pediatrics"],
            "immunizations": ["pediatrics"],
        }
        
        # Specialty synonyms
        self.specialty_synonyms = {
            "cardiology": ["cardio", "cardiac", "heart", "cardiologist", "cardiovascular"],
            "neurology": ["neuro", "neurological", "brain", "neurologist", "neural"],
            "gastroenterology": ["gastro", "GI", "digestive", "gastroenterologist"],
            "dermatology": ["derm", "dermatological", "skin", "dermatologist"],
            "orthopedics": ["ortho", "orthopedic", "bone", "joint", "orthopedist"],
            "pediatrics": ["peds", "pediatric", "child", "children", "pediatrician"],
            "endocrinology": ["endo", "endocrine", "hormone", "thyroid", "endocrinologist"],
            "urology": ["uro", "urological", "kidney", "urologist"],
            "psychiatry": ["psych", "psychiatric", "mental", "psychiatrist"],
            "oncology": ["onco", "oncological", "cancer", "tumor", "oncologist"],
        }
        
        # Common abbreviations
        self.abbreviations = {
            "cardio": "cardiology",
            "neuro": "neurology",
            "gastro": "gastroenterology",
            "derm": "dermatology",
            "ortho": "orthopedics",
            "peds": "pediatrics",
            "endo": "endocrinology",
            "uro": "urology",
            "psych": "psychiatry",
            "onco": "oncology",
            "GI": "gastroenterology",
            "CBT": "psychiatric eval",
            "EEG": "EEG",
            "EMG": "EMG",
        }
        
        # Typo corrections (Levenshtein-based)
        self.typo_corrections = {
            "cardiolog": "cardiology",
            "neorolog": "neurology",
            "gastroenterolgy": "gastroenterology",
            "drmatolgy": "dermatology",
            "orthopedics": "orthopedics",  # correct spelling
            "pediatrcs": "pediatrics",
            "endocrineology": "endocrinology",
            "urolog": "urology",
            "psyc": "psychiatry",
            "oncolog": "oncology",
        }
    
    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with synonyms and related medical terms.
        
        Args:
            query: Original search query
        
        Returns:
            List of expanded query variations
        """
        query_lower = query.lower()
        expansions = [query, query_lower]  # Keep original and lowercase
        
        # 1. Expand abbreviations
        for abbr, expansion in self.abbreviations.items():
            if abbr.lower() in query_lower:
                # Create expansion with abbreviation replaced
                expanded = query_lower.replace(abbr.lower(), expansion)
                if expanded not in expansions:
                    expansions.append(expanded)
        
        # 2. Expand symptoms to specialties
        for symptom, specialties in self.symptom_specialty_map.items():
            if symptom in query_lower:
                for spec in specialties:
                    expanded = query_lower.replace(symptom, spec)
                    if expanded not in expansions:
                        expansions.append(expanded)
        
        # 3. Expand procedures to specialties
        for procedure, specialties in self.procedure_specialty_map.items():
            if procedure.lower() in query_lower:
                for spec in specialties:
                    expanded = query_lower.replace(procedure.lower(), spec)
                    if expanded not in expansions:
                        expansions.append(expanded)
        
        # 4. Expand specialty synonyms
        for specialty, synonyms in self.specialty_synonyms.items():
            for syn in synonyms:
                if syn.lower() in query_lower:
                    # Add expansions with all synonyms
                    for alt_syn in synonyms:
                        if alt_syn.lower() != syn.lower():
                            expanded = query_lower.replace(syn.lower(), alt_syn)
                            if expanded not in expansions:
                                expansions.append(expanded)
        
        # 5. Try typo correction
        for typo, correct in self.typo_corrections.items():
            if typo.lower() in query_lower:
                expanded = query_lower.replace(typo.lower(), correct)
                if expanded not in expansions:
                    expansions.append(expanded)
        
        # 6. Add profession expansions (doctor → cardiologist, etc.)
        if "doctor" in query_lower or "specialist" in query_lower or "doctor" in query_lower:
            # Try to match with specialty names
            for specialty in self.specialty_synonyms.keys():
                if specialty in " ".join(expansions).lower():
                    for syn in self.specialty_synonyms[specialty]:
                        expanded = query_lower.replace("doctor", syn).replace("specialist", syn.replace("ology", "ologist"))
                        if expanded not in expansions and len(expanded) > 3:
                            expansions.append(expanded)
        
        # Remove duplicates and short strings
        expansions = [e for e in set(expansions) if len(e.strip()) > 0]
        
        # Sort by length (prefer more specific expansions)
        return sorted(expansions, key=len, reverse=True)
    
    def get_specialty_from_query(self, query: str) -> List[str]:
        """
        Extract specialty names from query.
        
        Args:
            query: Search query
        
        Returns:
            List of detected specialties
        """
        query_lower = query.lower()
        detected = []
        
        # Check symptom mappings
        for symptom, specialties in self.symptom_specialty_map.items():
            if symptom in query_lower:
                detected.extend(specialties)
        
        # Check procedure mappings
        for procedure, specialties in self.procedure_specialty_map.items():
            if procedure.lower() in query_lower:
                detected.extend(specialties)
        
        # Check specialty synonyms
        for specialty, synonyms in self.specialty_synonyms.items():
            for syn in synonyms:
                if syn.lower() in query_lower:
                    detected.append(specialty)
                    break
        
        # Return unique, in order
        return list(dict.fromkeys(detected))
    
    def get_skills_from_query(self, query: str) -> List[str]:
        """
        Extract skill names from query.
        
        Args:
            query: Search query
        
        Returns:
            List of detected skills
        """
        query_lower = query.lower()
        detected = []
        
        # Check procedure mappings (procedures are often skills)
        for procedure in self.procedure_specialty_map.keys():
            if procedure.lower() in query_lower:
                detected.append(procedure)
        
        return list(dict.fromkeys(detected))


# Testing
if __name__ == "__main__":
    expander = MedicalQueryExpander()
    
    test_queries = [
        "chest pain",
        "bone doctor",
        "cardiolog",
        "skin specialist with laser",
        "who does CBT",
        "GI doctor",
        "heart specialists",
    ]
    
    print("=" * 70)
    print("QUERY EXPANSION EXAMPLES")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\nOriginal: {query}")
        expansions = expander.expand_query(query)
        print(f"Expansions ({len(expansions)}):")
        for i, exp in enumerate(expansions[:5], 1):
            print(f"  {i}. {exp}")
        
        specialties = expander.get_specialty_from_query(query)
        skills = expander.get_skills_from_query(query)
        print(f"Detected specialties: {specialties}")
        print(f"Detected skills: {skills}")
