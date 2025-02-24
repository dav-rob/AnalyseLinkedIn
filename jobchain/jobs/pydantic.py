from typing import List

from pydantic import BaseModel


class JobAnalysis(BaseModel):
    """Job metadata model"""
    match_score: float
    strengths: List[str]
    gaps: List[str]
    detailed_analysis: str

