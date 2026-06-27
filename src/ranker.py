import heapq
from collections.abc import Iterable
from src.models import CandidateModel
from src.detectors.honeypot_detector import is_honeypot
from src.scorers.title_career_scorer import TitleCareerScorer
from src.scorers.skills_scorer import SkillsScorer
from src.scorers.behavioral_scorer import BehavioralScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.location_scorer import LocationScorer
from src.config import FICTIONAL_COMPANIES

class Ranker:
    def __init__(self):
        self.scorers = [
            TitleCareerScorer(weight=0.35),
            BehavioralScorer(weight=0.25),
            SkillsScorer(weight=0.20),
            ExperienceScorer(weight=0.10),
            LocationScorer(weight=0.10),
        ]

    def score_candidate(self, candidate: CandidateModel) -> tuple[float, str]:
        # Stage 1: Drop if current company is fictional
        if candidate.profile.current_company in FICTIONAL_COMPANIES:
            return 0.0, ""
            
        # Stage 1.5: Subtle honeypot methods
        if is_honeypot(candidate):
            return 0.0, ""
            
        total_score = 0.0
        for scorer in self.scorers:
            total_score += scorer(candidate)
            
        # Basic reasoning avoiding hallucination
        must_have_kws = ['embedding', 'sentence-transformers', 'bge', 'e5', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch', 'elasticsearch', 'faiss', 'vector database', 'python', 'ndcg', 'mrr', 'map', 'evaluation', 'a/b test']
        matched_skills = [s for s in candidate.skills if any(kw in s.name.lower() for kw in must_have_kws)]
        top_skills = sorted(matched_skills if matched_skills else candidate.skills, key=lambda s: s.duration_months, reverse=True)
        skill_str = " and ".join(s.name for s in top_skills[:2]) if top_skills else "AI technologies"
        reasoning = f"Strong fit: {candidate.profile.current_title} at {candidate.profile.current_company} with {candidate.profile.years_of_experience} YOE. Demonstrates deep expertise in {skill_str}."
        
        return round(total_score, 4), reasoning

    def rank(self, candidates: Iterable[CandidateModel], top_k: int = 100) -> list[tuple[float, CandidateModel, str]]:
        """
        Consumes the candidate stream, scores them, and returns the top_k.
        Uses a min-heap to bound memory usage to O(K) instead of O(N).
        """
        heap = []
        
        for candidate in candidates:
            score, reasoning = self.score_candidate(candidate)
            if score == 0.0:
                continue
                
            # Tie breaker by candidate_id ascending, but we want min-heap to pop the *worst* of the top K.
            # So if scores are equal, we pop the one with the *larger* candidate_id.
            # Therefore, we push (-candidate.candidate_id) so the larger ID (which is 'worse') is at the top.
            # Actually, simpler: push (score, -int(candidate_id.replace('CAND_','')), candidate)
            # Or just use a simple counter as tie breaker if we just want determinism.
            # For strict determinism: sort by score DESC, candidate_id ASC.
            # In a min-heap, the smallest item is at the root. We want to KEEP the largest scores.
            # So the min-heap should pop the SMALLEST score.
            # If scores are equal, we want to KEEP the SMALLEST candidate_id.
            # So the min-heap should pop the LARGEST candidate_id.
            # So our sort key for min-heap is (score, candidate.candidate_id) 
            # Wait, if score is the same, we want the LARGEST candidate_id to be at the top of the min-heap so it gets popped.
            # String comparison: "CAND_0000002" > "CAND_0000001".
            # So pushing (score, candidate.candidate_id, candidate) means the smaller ID is popped first?
            # No, if scores are equal, Python compares candidate_id.
            # The smaller candidate_id will be considered "smaller", so it will be at the root of the min-heap and popped.
            # But we want to KEEP the smaller candidate_id. We should pop the LARGER candidate_id.
            # To fix this, we can invert the candidate_id for comparison.
            # ID format is CAND_XXXXXXX
            try:
                id_num = int(candidate.candidate_id.split('_')[1])
                tie_breaker = -id_num
            except Exception:
                tie_breaker = 0
                
            item = (score, tie_breaker, candidate, reasoning)
            
            if len(heap) < top_k:
                heapq.heappush(heap, item)
            else:
                # push item, then pop the smallest
                heapq.heappushpop(heap, item)
                
        # The heap now contains the top_k items.
        # We need to sort them in descending order.
        heap.sort(key=lambda x: (x[0], x[1]), reverse=True)
        
        # Return score, candidate, and reasoning
        return [(score, candidate, reasoning) for score, tie, candidate, reasoning in heap]
