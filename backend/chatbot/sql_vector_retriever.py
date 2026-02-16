"""
SQL + Vector + Schedule-Aware Retriever

Three-stage retrieval pipeline:
1. SQL Filtering: Find doctors by specialty/skills/availability
2. Vector Ranking: Rank filtered doctors by semantic relevance
3. Schedule Boost: Prioritize doctors available soonest
"""

import sqlite3
import numpy as np
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from pathlib import Path

try:
    from vector_utils import init_embeddings
except ImportError:
    from .vector_utils import init_embeddings


class SQLVectorRetriever:
    """
    Advanced retriever combining SQL filtering, vector ranking, and schedule awareness.
    
    Workflow:
    1. SQL Stage: Filter doctors by specialty, skills, availability
    2. Vector Stage: Rank filtered doctors by semantic relevance
    3. Schedule Stage: Boost doctors available soonest
    """
    
    def __init__(
        self,
        db_path: str = "doctors.db",
        vector_store_dir: str = "./chroma_langchain_db",
        embedding_model: str = "text-embedding-3-small",
        use_vector_store: bool = True,
        max_candidates: int = 200,
        schedule_penalty_factor: float = 0.9,
        schedule_boosts: Optional[Dict[int, float]] = None,
        rerank_top_n: int = 5
    ):
        """
        Initialize SQL + Vector retriever.
        
        Args:
            db_path: Path to SQLite database
            vector_store_dir: Directory for vector store
            embedding_model: Embedding model name
            use_vector_store: Whether to use vector embeddings
        """
        self.db_path = db_path
        self.vector_store_dir = vector_store_dir
        self.embedding_model = embedding_model
        self.use_vector_store = use_vector_store
        self.max_candidates = max_candidates
        self.schedule_penalty_factor = schedule_penalty_factor
        self.schedule_boosts = schedule_boosts or {0: 0.25, 1: 0.15}
        self.rerank_top_n = rerank_top_n
        
        # Initialize components
        self._init_sql()
        self._load_reference_data()
        if use_vector_store:
            self._init_vector()
        
        print("[OK] SQL + Vector retriever initialized")
    
    def _init_sql(self):
        """Initialize SQL database connection."""
        db_path = Path(self.db_path)
        if not db_path.exists():
            # Search for database
            for parent in Path.cwd().parents:
                db_path = parent / self.db_path
                if db_path.exists():
                    break
        
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
        
        # Test connection
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = self.cursor.fetchone()[0]
        print(f"[OK] Connected to SQL database ({doctor_count} doctors)")
    
    def _init_vector(self):
        """Initialize vector embeddings client."""
        try:
            self.embeddings = init_embeddings(self.embedding_model)
            print("[OK] Embeddings client initialized")
        except Exception as e:
            print(f"[WARN] Vector store failed: {e}")
            self.use_vector_store = False

    def _load_reference_data(self):
        """Cache specialties and skills for fast matching."""
        self.cursor.execute("SELECT DISTINCT specialty FROM doctors")
        self.specialties = [row[0] for row in self.cursor.fetchall()]
        self.specialties_lower = {s.lower(): s for s in self.specialties}

        self.cursor.execute("SELECT DISTINCT skill FROM skills")
        self.skills = [row[0] for row in self.cursor.fetchall()]
        self.skills_lower = {s.lower(): s for s in self.skills}
    
    # ===== STAGE 1: SQL FILTERING =====
    
    def _extract_specialty_from_query(self, query: str) -> Optional[List[str]]:
        """
        Extract specialty keywords from query.
        
        Returns:
            List of specialties or None if not found
        """
        # Common medical terms mapping to specialties
        specialty_keywords = {
            "cardio|heart|cardiac|chest|cardiologist": ["cardiology"],
            "neuro|brain|nerve|seizure|neurologist": ["neurology"],
            "derm|skin|rash|acne|dermatologist": ["dermatology"],
            "gastro|gi|stomach|digestion|gastroenterologist": ["gastroenterology"],
            "ortho|bone|joint|fracture|orthopedist": ["orthopedics"],
            "psychia|mental|depression|anxiety|psychiatrist": ["psychiatry"],
            "endo|hormone|thyroid|diabetes|endocrinologist": ["endocrinology"],
            "pediatric|child|baby|infant|pediatrician": ["pediatrics"],
            "oncology|cancer|tumor|chemo|oncologist": ["oncology"],
            "urology|bladder|kidney|urologist": ["urology"],
        }
        
        query_lower = query.lower()
        found_specialties = []
        
        for keywords, specialties in specialty_keywords.items():
            if any(word in query_lower for word in keywords.split('|')):
                found_specialties.extend(specialties)

        # Direct specialty name match
        for spec_lower, spec in self.specialties_lower.items():
            if spec_lower in query_lower:
                found_specialties.append(spec)
        
        return list(set(found_specialties)) if found_specialties else None
    
    def _extract_skills_from_query(self, query: str) -> Optional[List[str]]:
        """
        Extract skill keywords from query.
        
        Returns:
            List of skills or None if not found
        """
        # Find which skills are mentioned in query
        query_lower = query.lower()
        found_skills = []

        for skill_lower, skill in self.skills_lower.items():
            if skill_lower in query_lower:
                found_skills.append(skill)
        
        return found_skills if found_skills else None
    
    def _get_available_doctors(self, specialty: Optional[List[str]] = None) -> List[int]:
        """
        Get doctor IDs with availability (any scheduled slot).
        
        Args:
            specialty: Optional list of specialties to filter by
        
        Returns:
            List of doctor IDs
        """
        if specialty:
            specialty_placeholders = ','.join('?' * len(specialty))
            query = f"""
            SELECT DISTINCT d.id
            FROM doctors d
            WHERE d.specialty IN ({specialty_placeholders})
            AND d.id IN (
                SELECT DISTINCT doctor_id FROM schedule
            )
            """
            self.cursor.execute(query, specialty)
        else:
            query = """
            SELECT DISTINCT d.id
            FROM doctors d
            WHERE d.id IN (
                SELECT DISTINCT doctor_id FROM schedule
            )
            """
            self.cursor.execute(query)
        
        return [row[0] for row in self.cursor.fetchall()]

    def _should_filter_by_availability(self, query: str) -> bool:
        """Decide if availability should be used as a hard filter."""
        query_lower = query.lower()
        keywords = ["available", "availability", "soon", "next", "schedule", "appointment"]
        return any(keyword in query_lower for keyword in keywords)
    
    def _get_doctors_with_skills(self, skills: List[str]) -> List[int]:
        """
        Get doctor IDs that have specified skills.
        
        Args:
            skills: List of skill names
        
        Returns:
            List of doctor IDs
        """
        skill_placeholders = ','.join('?' * len(skills))
        query = f"""
        SELECT DISTINCT doctor_id FROM skills
        WHERE skill IN ({skill_placeholders})
        """
        self.cursor.execute(query, skills)
        return [row[0] for row in self.cursor.fetchall()]
    
    def _sql_filter(self, query: str) -> List[Dict]:
        """
        Stage 1: SQL Filtering.
        
        Filter doctors by specialty, skills, and availability.
        
        Args:
            query: User search query
        
        Returns:
            List of filtered doctor records
        """
        # Extract specialty and skills from query
        specialties = self._extract_specialty_from_query(query)
        skills = self._extract_skills_from_query(query)
        
        # Get available doctors (primary filter only when requested)
        if self._should_filter_by_availability(query):
            if specialties:
                available_doc_ids = self._get_available_doctors(specialties)
            else:
                available_doc_ids = self._get_available_doctors()
        else:
            if specialties:
                specialty_placeholders = ','.join('?' * len(specialties))
                query_sql = f"SELECT id FROM doctors WHERE specialty IN ({specialty_placeholders})"
                self.cursor.execute(query_sql, specialties)
                available_doc_ids = [row[0] for row in self.cursor.fetchall()]
            else:
                self.cursor.execute("SELECT id FROM doctors")
                available_doc_ids = [row[0] for row in self.cursor.fetchall()]
        
        # If skills mentioned, intersect with skill-matching doctors
        if skills:
            skill_doc_ids = self._get_doctors_with_skills(skills)
            available_doc_ids = list(set(available_doc_ids) & set(skill_doc_ids))

        # Fallback: if availability filter is too restrictive, expand to all matching doctors
        if not available_doc_ids:
            if skills:
                available_doc_ids = self._get_doctors_with_skills(skills)
            elif specialties:
                specialty_placeholders = ','.join('?' * len(specialties))
                query = f"SELECT id FROM doctors WHERE specialty IN ({specialty_placeholders})"
                self.cursor.execute(query, specialties)
                available_doc_ids = [row[0] for row in self.cursor.fetchall()]
            else:
                self.cursor.execute("SELECT id FROM doctors")
                available_doc_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Get doctor details
        if not available_doc_ids:
            return []

        # Limit candidates for vector ranking
        if len(available_doc_ids) > self.max_candidates:
            available_doc_ids = available_doc_ids[:self.max_candidates]

        id_placeholders = ','.join('?' * len(available_doc_ids))
        query_sql = f"""
        SELECT id, name, specialty FROM doctors
        WHERE id IN ({id_placeholders})
        """
        self.cursor.execute(query_sql, available_doc_ids)
        
        doctors = []
        for row in self.cursor.fetchall():
            doctor_id = row[0]
            self.cursor.execute(
                "SELECT skill FROM skills WHERE doctor_id = ?",
                [doctor_id]
            )
            doctor_skills = [skill_row[0] for skill_row in self.cursor.fetchall()]

            doctors.append({
                "id": doctor_id,
                "name": row[1],
                "specialty": row[2],
                "skills": doctor_skills,
            })
        
        return doctors
    
    # ===== STAGE 2: VECTOR RANKING =====
    
    def _vector_rank(self, query: str, doctors: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        Stage 2: Vector Ranking.
        
        Rank doctors by semantic relevance using vector embeddings.
        
        Args:
            query: User search query
            doctors: List of doctor records to rank
        
        Returns:
            List of (doctor, similarity_score) tuples, sorted by score descending
        """
        if not self.use_vector_store or not doctors:
            # If no embeddings, return in original order with default score
            return [(doc, 0.5) for doc in doctors]

        # Build doctor texts for embedding
        doctor_texts = []
        for doctor in doctors:
            skills_text = ", ".join(doctor.get("skills", []))
            doctor_texts.append(f"{doctor['name']} {doctor['specialty']} {skills_text}")

        try:
            query_vec = self.embeddings.embed_query(query)
            doc_vecs = self.embeddings.embed_documents(doctor_texts)
        except Exception as e:
            print(f"[WARN] Embedding failed: {e}")
            return [(doc, 0.5) for doc in doctors]

        # Cosine similarity
        query_vec = np.array(query_vec)
        query_norm = np.linalg.norm(query_vec) + 1e-9

        ranked = []
        for doctor, doc_vec in zip(doctors, doc_vecs):
            doc_vec = np.array(doc_vec)
            score = float(np.dot(query_vec, doc_vec) / (query_norm * (np.linalg.norm(doc_vec) + 1e-9)))
            ranked.append((doctor, score))
        
        # Sort by score, descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
    
    # ===== STAGE 3: SCHEDULE BOOSTING =====
    
    def _get_next_available_slot(self, doctor_id: int) -> Optional[Dict]:
        """
        Get next available appointment slot for a doctor.
        
        Args:
            doctor_id: Doctor ID
        
        Returns:
            Dict with 'days_until', 'start_hour', 'day_of_week' or None
        """
        days_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                   4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        reverse_days = {v: k for k, v in days_map.items()}
        
        current_day_num = datetime.now().weekday()
        current_hour = datetime.now().hour
        
        self.cursor.execute(
            "SELECT day_of_week, start_hour, end_hour FROM schedule WHERE doctor_id = ?",
            [doctor_id]
        )
        
        schedule = self.cursor.fetchall()
        
        for row in schedule:
            day_name, start_hour, end_hour = row[0], row[1], row[2]
            day_num = reverse_days.get(day_name)
            
            if day_num is None:
                continue
            
            # Calculate days until this slot
            if day_num >= current_day_num:
                days_until = day_num - current_day_num
            else:
                days_until = 7 - current_day_num + day_num
            
            # If today, check if time already passed
            if days_until == 0 and start_hour <= current_hour:
                continue
            
            return {
                'days_until': days_until,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'day_of_week': day_name
            }
        
        return None
    
    def _schedule_rerank(
        self,
        ranked_doctors: List[Tuple[Dict, float]],
        apply_rerank: bool = False
    ) -> Tuple[List[Tuple[Dict, float]], Dict[int, Dict]]:
        """
        Stage 3: Availability-aware rerank.

        Reorders only the top-N results by next available slot while keeping
        semantic ranking intact for the rest. Returns a schedule cache for
        formatting output.
        """
        schedule_cache: Dict[int, Dict] = {}

        if not ranked_doctors:
            return [], schedule_cache

        if not apply_rerank:
            return ranked_doctors, schedule_cache

        top_n = min(self.rerank_top_n, len(ranked_doctors))
        top_slice = ranked_doctors[:top_n]
        remainder = ranked_doctors[top_n:]

        def availability_key(item: Tuple[Dict, float]) -> Tuple[int, int]:
            doctor, _ = item
            schedule = self._get_next_available_slot(doctor['id'])
            if schedule is None:
                schedule_cache[doctor['id']] = {'days_until': None}
                return (999, 99)

            schedule_cache[doctor['id']] = schedule
            return (schedule['days_until'], schedule['start_hour'])

        top_slice_sorted = sorted(top_slice, key=availability_key)
        return top_slice_sorted + remainder, schedule_cache
    
    # ===== MAIN RETRIEVAL =====
    
    def retrieve(self, query: str, k: int = 10) -> List[Dict]:
        """
        Full three-stage retrieval pipeline.
        
        Args:
            query: User search query
            k: Number of results to return
        
        Returns:
            List of doctor results with scores and availability
        """
        # Stage 1: SQL Filtering
        filtered_doctors = self._sql_filter(query)
        
        if not filtered_doctors:
            return []
        
        # Stage 2: Vector Ranking
        ranked_doctors = self._vector_rank(query, filtered_doctors)

        # Stage 3: Availability-aware rerank (top-N only)
        apply_rerank = self._should_filter_by_availability(query)
        reranked_doctors, schedule_cache = self._schedule_rerank(
            ranked_doctors,
            apply_rerank=apply_rerank
        )
        
        # Format results
        results = []
        for doctor, final_score in reranked_doctors[:k]:
            schedule = schedule_cache.get(doctor['id'])
            if schedule is None:
                schedule = self._get_next_available_slot(doctor['id'])
                if schedule is None:
                    schedule = {'days_until': None}
            result = {
                'id': doctor['id'],
                'name': doctor['name'],
                'specialty': doctor['specialty'],
                'skills': doctor.get('skills', []),
                'relevance_score': round(final_score, 3),
                'next_available': schedule
            }
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get retriever statistics."""
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(DISTINCT specialty) FROM doctors")
        specialty_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM skills")
        skill_count = self.cursor.fetchone()[0]
        
        return {
            'total_doctors': doctor_count,
            'total_specialties': specialty_count,
            'total_skills': skill_count,
            'uses_vector_search': self.use_vector_store
        }


# ===== TESTING =====

if __name__ == "__main__":
    import time
    
    # Initialize retriever
    print("="*70)
    print("SQL + VECTOR + SCHEDULE-AWARE RETRIEVER TEST")
    print("="*70)
    
    retriever = SQLVectorRetriever()
    
    print("\nRetriever Statistics:")
    stats = retriever.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test queries
    test_queries = [
        "I have chest pain",
        "who does CBT for depression",
        "bone doctor with surgery skills",
        "cardiologist available soon",
    ]
    
    print("\n" + "="*70)
    print("TEST QUERIES")
    print("="*70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        start = time.time()
        results = retriever.retrieve(query, k=5)
        latency = (time.time() - start) * 1000
        
        print(f"Results ({latency:.1f}ms):")
        if results:
            for i, doctor in enumerate(results, 1):
                next_avail = doctor.get('next_available', {})
                days = next_avail.get('days_until')
                avail_str = f"available in {days} days" if days is not None else "no availability"
                print(f"  {i}. {doctor['name']} ({doctor['specialty']}) - Score: {doctor['relevance_score']}, {avail_str}")
        else:
            print("  No doctors found")
