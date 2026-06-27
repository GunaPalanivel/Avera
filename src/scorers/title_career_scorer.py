from src.models import CandidateModel
from src.scorers.base import BaseScorer

class TitleCareerScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        # Title Tiering (max 0.5)
        title_score = 0.0
        current_title = candidate.profile.current_title.lower()
        
        if 'junior' in current_title:
            title_score = 0.0
        elif 'ai engineer' in current_title or 'machine learning' in current_title or 'ml engineer' in current_title:
            if 'senior' in current_title or 'lead' in current_title or 'principal' in current_title or 'staff' in current_title:
                title_score = 0.5
            else:
                title_score = 0.4
        elif 'data scientist' in current_title:
            title_score = 0.1
        elif 'software engineer' in current_title:
            title_score = 0.2
            
        # Company Quality (max 0.3)
        company_score = 0.3
        consulting_firms = {'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini', 'ibm'}
        
        career = candidate.career_history
        all_companies = [c.company.lower() for c in career]
        
        consulting_count = sum(1 for c in all_companies if any(f in c for f in consulting_firms))
        if consulting_count == len(all_companies) and len(all_companies) > 0:
            # Consulting only
            company_score = 0.1
        elif consulting_count > 0:
            # Mixed
            company_score = 0.25
            
        # Job Hopping (max 0.2)
        hopping_score = 0.2
        if len(career) > 1:
            total_months = sum(c.duration_months for c in career)
            avg_months = total_months / len(career)
            if avg_months < 18:
                hopping_score = 0.0  # Penalty for <1.5 years
            elif avg_months < 24:
                hopping_score = 0.1
                
        return title_score + company_score + hopping_score
