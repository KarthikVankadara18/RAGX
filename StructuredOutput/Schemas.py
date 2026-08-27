from pydantic import BaseModel

class CandidateAnalysis(BaseModel):
    name: str
    skills: list[str]
    experience: str
    score: bool
    reason: str
