from src.config import FICTIONAL_COMPANIES
from src.models import CandidateModel

AI_KEYWORDS = {
    "rag",
    "llm",
    "machine learning",
    "artificial intelligence",
    "deep learning",
    "embeddings",
    "vector database",
    "pinecone",
    "langchain",
}

NON_TECH_TITLES = {
    "hr manager",
    "accountant",
    "sales executive",
    "content writer",
    "customer support",
    "marketing manager",
    "civil engineer",
    "mechanical engineer",
    "graphic designer",
    "operations manager",
}


def is_honeypot(candidate: CandidateModel) -> bool:
    """
    Returns True if the candidate is identified as a honeypot via subtle rules.
    (Note: current_company fictional drop is done upstream in Stage 1).
    """
    title = candidate.profile.current_title.lower()
    yoe = candidate.profile.years_of_experience
    skills = candidate.skills
    career = candidate.career_history

    # Method 1: Title/skill mismatch (non-tech title with many AI skills)
    if any(non_tech in title for non_tech in NON_TECH_TITLES):
        ai_skill_count = sum(1 for s in skills if any(ai_kw in s.name.lower() for ai_kw in AI_KEYWORDS))
        if ai_skill_count >= 5:
            return True

    # Method 2: Expert proficiency with 0 months duration
    expert_zero_count = sum(1 for s in skills if s.proficiency == "expert" and s.duration_months == 0)
    if expert_zero_count >= 3:
        return True

    # Method 3: Impossible seniority
    if "senior" in title and yoe < 2:
        return True
    if "junior" in title and yoe > 10:
        return True



    # Method 5: Extremely high skill count with no assessments
    assessment_scores = candidate.redrob_signals.skill_assessment_scores
    if len(skills) > 15 and len(assessment_scores) == 0:
        senior_title = any(k in title for k in ("senior", "lead", "principal", "staff"))
        if not (senior_title and yoe >= 5):
            return True

    return False
