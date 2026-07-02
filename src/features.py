from datetime import date
from models import Candidate

TODAY = date(2026, 6, 29)

TITLE_TIER_1 = {
    "senior ai engineer", "lead ai engineer", "staff machine learning engineer",
    "senior machine learning engineer", "senior nlp engineer", "search engineer",
    "recommendation systems engineer", "senior applied scientist"
}

TITLE_TIER_2 = {
    "ai engineer", "ml engineer", "machine learning engineer", "nlp engineer",
    "ai research engineer", "applied ml engineer", "senior data scientist",
    "data scientist", "ai specialist", "senior software engineer (ml)",
    "junior ml engineer"
}

TITLE_TIER_3 = {
    "senior data engineer", "data engineer", "analytics engineer",
    "data analyst", "senior software engineer", "software engineer",
    "backend engineer", "full stack developer", "devops engineer"
}

TARGET_SKILLS = {
    "embeddings", "sentence transformers", "faiss", "pinecone", "weaviate",
    "qdrant", "milvus", "opensearch", "elasticsearch", "python",
    "learning to rank", "bm25", "information retrieval",
    "recommendation systems", "lora", "qlora", "peft", "fine-tuning llms",
    "rag", "nlp", "natural language processing", "mlops"
}

TARGET_LOCATIONS_TIER1 = {"pune", "noida"}
TARGET_LOCATIONS_TIER2 = {"hyderabad", "mumbai", "delhi", "gurgaon"}

def title_score(c: Candidate) -> float:
    titles = [t.lower().strip() for t in c.all_titles()]
    if not titles:
        return 0.0

    def tier_of(t):
        if t in TITLE_TIER_1:
            return 3
        if t in TITLE_TIER_2:
            return 2
        if t in TITLE_TIER_3:
            return 1
        return 0

    current_tier = tier_of(titles[0])

    if len(titles) > 1:
        past_tiers = [tier_of(t) for t in titles[1:]]
        past_avg = sum(past_tiers) / len(past_tiers)
    else:
        past_avg = current_tier

    combined = 0.7 * current_tier + 0.3 * past_avg
    return min(combined / 3.0, 1.0)

def skill_evidence_score(c: Candidate) -> float:
    candidate_skills = c.skill_names_lower()
    matched = candidate_skills & TARGET_SKILLS
    if not matched:
        return 0.0

    career_text_lower = c.career_text().lower()
    evidenced = 0
    for skill in matched:
        if skill in career_text_lower:
            evidenced += 1

    breadth = min(len(matched) / 8.0, 1.0)
    evidence_ratio = evidenced / len(matched)
    return min(breadth * (0.35 + 0.65 * evidence_ratio), 1.0)


def experience_band_score(c: Candidate) -> float:
    yoe = c.profile.years_of_experience
    if 5 <= yoe <= 9:
        return 1.0
    if yoe < 5:
        gap = 5 - yoe
        return max(0.0, 1.0 - gap / 4.0)
    gap = yoe - 9
    return max(0.0, 1.0 - gap / 10.0)


def location_score(c: Candidate) -> float:
    loc = c.profile.location.lower()
    country = c.profile.country.lower()
    willing = c.redrob_signals.willing_to_relocate if c.redrob_signals else False

    if country != "india":
        return 0.15

    if any(t in loc for t in TARGET_LOCATIONS_TIER1):
        return 1.0
    if any(t in loc for t in TARGET_LOCATIONS_TIER2):
        return 0.85
    return 0.70 if willing else 0.45


def education_score(c: Candidate) -> float:
    if not c.education:
        return 0.5
    tier_map = {
        "tier_1": 1.0,
        "tier_2": 0.8,
        "tier_3": 0.6,
        "tier_4": 0.4,
        "unknown": 0.5
    }
    scores = [tier_map.get(e.tier, 0.5) for e in c.education]
    return max(scores)