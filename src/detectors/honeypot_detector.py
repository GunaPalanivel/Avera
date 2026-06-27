from src.models import CandidateModel

FICTIONAL_COMPANIES = {
    "stark industries",
    "pied piper",
    "acme corp",
    "dunder mifflin",
    "wayne enterprises",
    "initech",
    "umbrella corp",
    "hooli",
    "massive dynamic",
    "cyberdyne systems",
    "tyrell corporation"
}

AI_KEYWORDS = {
    "rag",
    "llm",
    "machine learning",
    "artificial intelligence",
    "deep learning",
    "embeddings",
    "vector database",
    "pinecone",
    "langchain"
}

def is_honeypot(candidate: CandidateModel) -> bool:
    """
    Returns True if the candidate is identified as a honeypot (fake data).
    """
    # Rule 1: Fictional company in career history
    for entry in candidate.career_history:
        company_lower = entry.company.lower()
        if any(fictional in company_lower for fictional in FICTIONAL_COMPANIES):
            return True
            
    # Rule 2: Marketing Manager with AI keywords (JD L74 trap)
    title_lower = candidate.profile.current_title.lower()
    if "marketing" in title_lower:
        skill_names = {s.name.lower() for s in candidate.skills}
        if any(ai_skill in skill for skill in skill_names for ai_skill in AI_KEYWORDS):
            return True

    # Rule 3: Expert proficiency with 0 months duration
    for skill in candidate.skills:
        if skill.proficiency == "expert" and skill.duration_months == 0:
            return True

    return False
