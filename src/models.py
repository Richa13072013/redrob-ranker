from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List


def parse_date(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()

@dataclass
class CareerEntry:
    company: str
    title: str
    start_date: Optional[date]
    end_date: Optional[date]
    duration_months: int
    is_current: bool
    industry: str
    company_size: str
    description: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            company=d.get("company", ""),
            title=d.get("title", ""),
            start_date=parse_date(d.get("start_date")),
            end_date=parse_date(d.get("end_date")),
            duration_months=int(d.get("duration_months") or 0),
            is_current=bool(d.get("is_current", False)),
            industry=d.get("industry", ""),
            company_size=d.get("company_size", ""),
            description=d.get("description", "") or ""
        )


@dataclass
class Skill:
    name: str
    proficiency: str
    endorsements: int
    duration_months: Optional[int]

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get("name", ""),
            proficiency=d.get("proficiency", ""),
            endorsements=int(d.get("endorsements") or 0),
            duration_months=d.get("duration_months")
        )


@dataclass
class EducationEntry:
    institution: str
    degree: str
    field_of_study: str
    start_year: Optional[int]
    end_year: Optional[int]
    grade: Optional[str]
    tier: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            institution=d.get("institution", ""),
            degree=d.get("degree", ""),
            field_of_study=d.get("field_of_study", ""),
            start_year=d.get("start_year"),
            end_year=d.get("end_year"),
            grade=d.get("grade"),
            tier=d.get("tier", "unknown")
        )


@dataclass
class Profile:
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: str
    current_industry: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            anonymized_name=d.get("anonymized_name", ""),
            headline=d.get("headline", ""),
            summary=d.get("summary", "") or "",
            location=d.get("location", ""),
            country=d.get("country", ""),
            years_of_experience=float(d.get("years_of_experience") or 0.0),
            current_title=d.get("current_title", ""),
            current_company=d.get("current_company", ""),
            current_company_size=d.get("current_company_size", ""),
            current_industry=d.get("current_industry", "")
        )


@dataclass
class RedrobSignals:
    profile_completeness_score: float
    signup_date: Optional[date]
    last_active_date: Optional[date]
    open_to_work_flag: bool
    profile_views_received_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: float
    skill_assessment_scores: dict
    connection_count: int
    endorsements_received: int
    notice_period_days: int
    expected_salary_min_lpa: float
    expected_salary_max_lpa: float
    preferred_work_mode: str
    willing_to_relocate: bool
    github_activity_score: float
    search_appearance_30d: int
    saved_by_recruiters_30d: int
    interview_completion_rate: float
    offer_acceptance_rate: float
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool

    @classmethod
    def from_dict(cls, d):
        salary = d.get("expected_salary_range_inr_lpa") or {}
        return cls(
            profile_completeness_score=float(d.get("profile_completeness_score") or 0.0),
            signup_date=parse_date(d.get("signup_date")),
            last_active_date=parse_date(d.get("last_active_date")),
            open_to_work_flag=bool(d.get("open_to_work_flag", False)),
            profile_views_received_30d=int(d.get("profile_views_received_30d") or 0),
            applications_submitted_30d=int(d.get("applications_submitted_30d") or 0),
            recruiter_response_rate=float(d.get("recruiter_response_rate") or 0.0),
            avg_response_time_hours=float(d.get("avg_response_time_hours") or 0.0),
            skill_assessment_scores=d.get("skill_assessment_scores") or {},
            connection_count=int(d.get("connection_count") or 0),
            endorsements_received=int(d.get("endorsements_received") or 0),
            notice_period_days=int(d.get("notice_period_days") or 0),
            expected_salary_min_lpa=float(salary.get("min") or 0.0),
            expected_salary_max_lpa=float(salary.get("max") or 0.0),
            preferred_work_mode=d.get("preferred_work_mode", ""),
            willing_to_relocate=bool(d.get("willing_to_relocate", False)),
            github_activity_score=float(d.get("github_activity_score") if d.get("github_activity_score") is not None else -1.0),
            search_appearance_30d=int(d.get("search_appearance_30d") or 0),
            saved_by_recruiters_30d=int(d.get("saved_by_recruiters_30d") or 0),
            interview_completion_rate=float(d.get("interview_completion_rate") or 0.0),
            offer_acceptance_rate=float(d.get("offer_acceptance_rate") if d.get("offer_acceptance_rate") is not None else -1.0),
            verified_email=bool(d.get("verified_email", False)),
            verified_phone=bool(d.get("verified_phone", False)),
            linkedin_connected=bool(d.get("linkedin_connected", False))
        )


@dataclass
class Candidate:
    candidate_id: str
    profile: Profile
    career_history: List[CareerEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    certifications: list = field(default_factory=list)
    languages: list = field(default_factory=list)
    redrob_signals: Optional[RedrobSignals] = None

    @classmethod
    def from_dict(cls, d):
        return cls(
            candidate_id=d["candidate_id"],
            profile=Profile.from_dict(d.get("profile", {})),
            career_history=[CareerEntry.from_dict(c) for c in d.get("career_history", [])],
            education=[EducationEntry.from_dict(e) for e in d.get("education", [])],
            skills=[Skill.from_dict(s) for s in d.get("skills", [])],
            certifications=d.get("certifications", []) or [],
            languages=d.get("languages", []) or [],
            redrob_signals=RedrobSignals.from_dict(d.get("redrob_signals", {}))
        )

    def all_titles(self):
        titles = [self.profile.current_title]
        titles += [c.title for c in self.career_history]
        return titles

    def skill_names_lower(self):
        return {s.name.lower() for s in self.skills}

    def career_text(self):
        parts = [self.profile.headline, self.profile.summary]
        for c in self.career_history:
            parts.append(f"{c.title} at {c.company}. {c.description}")
        return " ".join(p for p in parts if p)