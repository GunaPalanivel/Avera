from src.models import CandidateModel
from src.scorers.base import BaseScorer

class SkillsScorer(BaseScorer):
    MUST_HAVE = {
        'embeddings': ['embedding', 'sentence-transformers', 'bge', 'e5'],
        'vector_db': ['pinecone', 'weaviate', 'qdrant', 'milvus', 'opensearch', 'elasticsearch', 'faiss', 'vector database'],
        'python': ['python'],
        'eval': ['ndcg', 'mrr', 'map', 'evaluation', 'a/b test']
    }
    
    NICE_TO_HAVE = ['llm fine-tuning', 'lora', 'peft', 'qlora', 'xgboost', 'learning to rank', 'ltr']

    def score(self, candidate: CandidateModel) -> float:
        # Extract self-reported skills
        self_reported = {s.name.lower(): s for s in candidate.skills}
        
        # Extract assessed skills
        assessed_skills = {k.lower(): v for k, v in candidate.redrob_signals.skill_assessment_scores.items()}
        
        total_score = 0.0
        
        # Check MUST_HAVE (max 0.7)
        must_have_count = 0
        for category, keywords in self.MUST_HAVE.items():
            category_found = False
            
            for keyword in keywords:
                # Check assessed first (3x weight logic embedded in scoring limits)
                if any(keyword in a for a in assessed_skills):
                    must_have_count += 1
                    category_found = True
                    break
                    
                # Check self-reported
                if any(keyword in s for s in self_reported):
                    # Only add 0.5 for self reported, 1.0 for assessed
                    must_have_count += 0.5
                    category_found = True
                    break
                    
            if category_found and must_have_count >= 4:
                break
                
        # Normalize must have score to 0.7
        # Max possible must_have_count is 4 if all assessed.
        must_have_score = min(0.7, (must_have_count / 4.0) * 0.7)
        
        # Check NICE_TO_HAVE (max 0.3)
        nice_count = 0
        for keyword in self.NICE_TO_HAVE:
            if any(keyword in a for a in assessed_skills):
                nice_count += 1
            elif any(keyword in s for s in self_reported):
                nice_count += 0.5
                
        nice_score = min(0.3, (nice_count / 2.0) * 0.3)
        
        return must_have_score + nice_score
