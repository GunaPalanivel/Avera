from datetime import datetime, timezone
from src.models import CandidateModel
from src.scorers.base import BaseScorer

class BehavioralScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        sigs = candidate.redrob_signals
        
        # Availability (max 0.6)
        availability_score = 0.6
        
        # Recruiter response rate penalty
        resp_rate = sigs.recruiter_response_rate
        if resp_rate < 0.05:
            availability_score -= 0.4
        elif resp_rate < 0.2:
            availability_score -= 0.2
            
        # Inactivity penalty
        # Assume "now" is around Nov 2025 based on dataset context, or use standard diff
        # Let's parse last_active_date
        try:
            last_active = datetime.strptime(sigs.last_active_date, "%Y-%m-%d")
            # In our dataset context, the date is 2025. 
            # We'll use relative to 2026-01-01 for safety if it's late 2025.
            # Actually, just use hardcoded difference from "2026-06-27" (current date in scenario)
            now = datetime(2026, 6, 27)
            months_inactive = (now - last_active).days / 30.0
            
            if months_inactive > 6:
                availability_score -= 0.4
        except ValueError:
            pass
            
        availability_score = max(0.0, availability_score)
        
        # Notice Period (max 0.4)
        notice = sigs.notice_period_days
        notice_score = 0.0
        
        if notice <= 30:
            notice_score = 0.4
        elif notice <= 60:
            notice_score = 0.2
        else:
            notice_score = 0.0
            
        return availability_score + notice_score
