from src.models import CandidateModel
from src.scorers.base import BaseScorer

class LocationScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        location = candidate.profile.location.lower()
        
        if 'noida' in location or 'pune' in location:
            return 1.0
            
        if candidate.redrob_signals.willing_to_relocate:
            return 0.8
            
        return 0.0
