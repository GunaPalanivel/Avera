from src.config import NLP_IR_TERMS
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

DOMAIN_BUCKETS: dict[str, frozenset[str]] = {
    "cv": frozenset({"computer vision", "opencv", "object detection", "image classification", "yolo", "segmentation", "gans"}),
    "nlp": frozenset({"nlp", "llm", "embeddings", "rag", "sentence transformers", "information retrieval", "bert"}),
    "speech": frozenset({"speech recognition", "asr", "tts", "text to speech"}),
    "robotics": frozenset({"robotics", "slam", "autonomous"}),
}


def _skill_domain_bucket(skill_name: str) -> str | None:
    name = skill_name.lower()
    for bucket, terms in DOMAIN_BUCKETS.items():
        if any(term in name for term in terms):
            return bucket
    return None


def _has_nlp_ir_exposure(skills: list) -> bool:
    for s in skills:
        name = s.name.lower()
        if any(term in name for term in NLP_IR_TERMS):
            return True
    return False


def is_honeypot(candidate: CandidateModel) -> bool:
    """
    Returns True if the candidate is identified as a honeypot via subtle rules.
    (Note: current_company fictional drop is done upstream in Stage 1).
    """
    title = candidate.profile.current_title.lower()
    yoe = candidate.profile.years_of_experience
    skills = candidate.skills

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

    # Method 4: Multi-domain expert trap (expert in 3+ disjoint domains with thin backing)
    assessment_scores = candidate.redrob_signals.skill_assessment_scores
    expert_buckets: set[str] = set()
    expert_duration = 0
    for s in skills:
        if s.proficiency not in ("expert", "advanced"):
            continue
        bucket = _skill_domain_bucket(s.name)
        if bucket is None:
            continue
        expert_buckets.add(bucket)
        expert_duration += s.duration_months or 0

    if len(expert_buckets) >= 3:
        has_assessments = len(assessment_scores) > 0
        senior_backed = yoe >= 5 and has_assessments
        thin_duration = expert_duration < 36
        if not senior_backed and (thin_duration or not has_assessments):
            if not _has_nlp_ir_exposure(skills):
                return True

    # Method 5: Unverified generalist (extremely high skill count with no assessments)
    if len(skills) > 15 and len(assessment_scores) == 0:
        senior_title = any(k in title for k in ("senior", "lead", "principal", "staff"))
        if not (senior_title and yoe >= 5):
            return True

    return False
