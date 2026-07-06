from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class StrengthWeaknessItem(BaseModel):
    title: str = Field(..., description="Short bold title of the strength or weakness.")
    description: str = Field(..., description="A detailed explanation citing specific systems, tools, metrics, or mechanics. Avoid generic comments.")

class EvidenceItem(BaseModel):
    source: str = Field(..., description="The name of the source (e.g. 'Earnings Call Q1 2026', 'App Store Reviews', 'Tech Blog', 'Executive Interview', 'PR Announcement').")
    date: str = Field(..., description="Estimated date of the publication/data in format 'Month Year' (e.g., 'Jun 2026').")
    title: str = Field(..., description="Bold summary statement highlighting a specific, concrete finding with metrics or exact mechanisms (e.g. 'Allows GPTBot to index catalogue in robots.txt' or '4.7★ App Store rating across 125k reviews'). Avoid generic statements.")
    description: str = Field(..., description="A highly detailed, 3-4 sentence explanation of the specific context, metrics, and evidence found. It MUST include concrete figures (percentages, ratings, counts), specific feature mechanisms (e.g. checkout trade-in loops), or user complaints/praises. Generic summaries like 'high engagement' or 'good experience' are strictly disallowed.")

class PillarEvaluation(BaseModel):
    pillar_number: int = Field(..., description="The index of the pillar, from 1 to 8.")
    pillar_name: str = Field(..., description="The name of the growth capability pillar.")
    score: float = Field(..., description="Maturity score from 1.0 to 10.0.")
    maturity_label: str = Field(..., description="Maturity label corresponding to score range: 1.0-3.0 (Nascent), 4.0-7.0 (Developing), 8.0-10.0 (Leading).")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0 based on available information.")
    score_rationale: str = Field(..., description="Concise, 1-2 sentence score rationale explaining the core why behind the score.")
    strengths: List[StrengthWeaknessItem] = Field(..., description="List of key strengths identified (minimum 2).")
    weaknesses: List[StrengthWeaknessItem] = Field(..., description="List of key weaknesses/gaps identified (minimum 2).")
    supporting_evidence: List[EvidenceItem] = Field(..., description="List of specific sources and supporting evidence items found during research.")

class DiscoveredBestPractice(BaseModel):
    pillar_number: int = Field(..., description="The pillar index (1 to 8) under which this best practice falls.")
    pillar_name: str = Field(..., description="The name of the growth capability pillar.")
    description: str = Field(..., description="What the company does that is exemplary and sets a benchmark.")
    implementation_details: str = Field(..., description="Technical or process implementation details of this best practice.")

class CompanyEvaluation(BaseModel):
    company_name: str = Field(..., description="Name of the company evaluated.")
    industry: str = Field(..., description="The industry sector of the company.")
    overall_score: float = Field(..., description="The calculated average or holistic growth capability score from 1.0 to 10.0.")
    summary: str = Field(..., description="High-level synthesis of the company's growth capabilities in the AI age.")
    pillars: List[PillarEvaluation] = Field(..., description="Detailed scoring breakdown for each of the 8 pillars.")
    biggest_opportunities: List[str] = Field(..., description="Top opportunities (minimum 3) for the company to accelerate growth in the AI era.")
    biggest_challenges: List[str] = Field(..., description="Top challenges/risks (minimum 3) the company faces.")
    discovered_best_practices: List[DiscoveredBestPractice] = Field(
        default=[],
        description="Any outstanding, state-of-the-art growth capabilities discovered during evaluation that can serve as future benchmarks."
    )

class TelemetryData(BaseModel):
    domain: str
    robots_txt_bot_block_status: Dict[str, str] = Field(
        default={}, 
        description="AI crawlers allowed or blocked, e.g. {'GPTBot': 'allowed', 'PerplexityBot': 'blocked'}"
    )
    marketing_tech_stack: List[str] = Field(
        default=[], 
        description="Detected tools for personalization, analytics, attribution, or CDPs."
    )
    app_rating: Optional[float] = Field(default=None, description="App Store/Google Play rating if applicable.")
    app_rating_count: Optional[int] = Field(default=None, description="App Store/Google Play rating count.")
    api_docs_found: bool = Field(default=False, description="Whether public API developer portals were discovered.")
    aeo_visibility_citations: Optional[int] = Field(
        default=None, 
        description="Simulated AEO Citations index (number of times referenced in AI response citations per 100 queries)."
    )

class AnalysisRequest(BaseModel):
    company_name: str
    custom_context: Optional[str] = None
