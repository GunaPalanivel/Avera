from src.models import CandidateModel
from src.scorers.base import BaseScorer

class LocationScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        location = candidate.profile.location.lower()
        country = candidate.profile.country.lower() if candidate.profile.country else ""
        
        score = 0.0
        
        if 'india' in country or 'india' in location:
            score = max(score, 0.4)
            
        if candidate.redrob_signals.willing_to_relocate:
            score = max(score, 0.8)
            
        tier_1 = ['bangalore', 'bengaluru', 'hyderabad', 'chennai', 'mumbai', 'delhi', 'gurgaon', 'gurugram']
        if any(t in location for t in tier_1):
            score = max(score, 0.8)
            
        if 'noida' in location or 'pune' in location:
            score = max(score, 1.0)
            
        return score
