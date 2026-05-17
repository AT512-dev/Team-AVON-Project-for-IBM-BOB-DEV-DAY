from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from bob_core.schemas import DependencyIntelligencePayload, IntelligenceRequest, OnboardPayload, RoadmapStep
from bob_core.bob_service import generate_explanation, generate_checkpoint_quiz
from engine.dependency_intelligence import build_dependency_intelligence
from engine.parser import parse_repository

app = FastAPI(title="Compass AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OnboardRequest(BaseModel):
    repo_path: str
    task_description: Optional[str] = "Understand the codebase architecture"

@app.post("/api/v1/dependency-intelligence", response_model=DependencyIntelligencePayload)
async def dependency_intelligence(request: IntelligenceRequest):
    try:
        return build_dependency_intelligence(
            request.repo_path,
            include_tests=bool(request.include_tests),
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Dependency intelligence failed: {str(exc)}")

@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    try:
        intelligence = build_dependency_intelligence(request.repo_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository intelligence failed: {str(exc)}")

    roadmap_steps = []
    primary_file_content = ""

    for item in intelligence.roadmap:
        try:
            file_context = (
                f"File: {item.file}\n"
                f"Layer: {item.architectural_layer}\n"
                f"Complexity: {item.complexity_score}\n"
                f"Dependency radius: {item.dependency_radius}\n"
                f"Dependencies: {', '.join(item.prerequisites)}"
            )
            if not primary_file_content:
                primary_file_content = file_context
            learning_objective = await generate_explanation(file_context, request.task_description or "Understand the codebase architecture")
        except Exception:
            learning_objective = item.learning_reason

        roadmap_steps.append(
            RoadmapStep(
                file_path=item.file,
                complexity_score=item.complexity_score,
                learning_objective=learning_objective
            )
        )

    try:
        quiz = await generate_checkpoint_quiz(primary_file_content)
    except Exception:
        quiz = {"questions": []}

    return OnboardPayload(roadmap=roadmap_steps, quiz=quiz)

@app.get("/api/v1/repo-map")
async def repo_map(repo_path: str):
    try:
        return parse_repository(repo_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository parsing failed: {str(exc)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Compass AI"}
