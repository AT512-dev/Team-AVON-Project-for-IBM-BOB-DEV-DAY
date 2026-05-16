from typing import Dict, List, Any, Optional

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in self.__class__.__dict__.items():
                if key.startswith("_") or callable(value):
                    continue
                if key not in kwargs:
                    setattr(self, key, value() if callable(value) else value)
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self):
            def dump(value):
                if hasattr(value, "model_dump"):
                    return value.model_dump()
                if isinstance(value, list):
                    return [dump(item) for item in value]
                if isinstance(value, dict):
                    return {key: dump(item) for key, item in value.items()}
                return value

            return {
                key: dump(value)
                for key, value in self.__dict__.items()
                if not key.startswith("_")
            }

        def dict(self):
            return self.model_dump()

    def Field(default=None, default_factory=None):
        if default_factory is not None:
            return default_factory
        return default

class RepoMap(BaseModel):
    files: Dict[str, List[str]]

class RoadmapStep(BaseModel):
    file_path: str
    complexity_score: Any
    learning_objective: str

class OnboardPayload(BaseModel):
    roadmap: List[RoadmapStep]
    quiz: Any

class DependencyNode(BaseModel):
    id: str
    file: str
    label: str
    extension: str
    loc: int
    imports_count: int
    exports_count: int
    incoming_dependency_count: int
    outgoing_dependency_count: int
    downstream_impact: int
    dependency_radius: int
    complexity_score: int
    importance_score: int
    architectural_layer: str
    recommended_learning_order: int
    dependencies: List[str]
    dependents: List[str]
    symbols: List[str] = Field(default_factory=list)

class DependencyEdge(BaseModel):
    source: str
    target: str
    relationship: str = "imports"

class RoadmapItem(BaseModel):
    step: int
    file: str
    architectural_layer: str
    complexity_score: int
    dependency_radius: int
    learning_reason: str
    prerequisites: List[str]

class ClusterSummary(BaseModel):
    layer: str
    files: List[str]

class IntelligenceSummary(BaseModel):
    total_files: int
    total_edges: int
    circular_dependency_count: int
    architectural_layers: Dict[str, int]
    foundational_files: List[str]
    hub_files: List[str]
    risky_files: List[str]

class DependencyIntelligencePayload(BaseModel):
    repository: str
    summary: IntelligenceSummary
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    roadmap: List[RoadmapItem]
    clusters: List[ClusterSummary]
    circular_dependencies: List[List[str]]
    adjacency: Dict[str, List[str]]
    reverse_adjacency: Dict[str, List[str]]

class IntelligenceRequest(BaseModel):
    repo_path: str
    include_tests: Optional[bool] = False
