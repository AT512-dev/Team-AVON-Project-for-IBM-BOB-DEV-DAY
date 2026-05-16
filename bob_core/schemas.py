from pydantic import BaseModel
from typing import Dict, List, Any

class RepoMap(BaseModel):
    files: Dict[str, List[str]]

class RoadmapStep(BaseModel):
    file_path: str
    complexity_score: str
    learning_objective: str

class OnboardPayload(BaseModel):
    roadmap: List[RoadmapStep]
    quiz: Any