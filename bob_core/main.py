from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from bob_core.schemas import OnboardPayload, RoadmapStep
from bob_core.bob_service import generate_explanation, generate_checkpoint_quiz
from engine.parser import parse_repository
from engine.metrics import compute_complexity

app = FastAPI(title="Compass AI", version="1.0.0")

class OnboardRequest(BaseModel):
    repo_path: str
    task_description: Optional[str] = "Understand the codebase architecture"

@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    try:
        repo_map = parse_repository(request.repo_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository parsing failed: {str(exc)}")

    roadmap_steps = []
    primary_file_content = ""

    for file_path, imports in repo_map.files.items():
        complexity_score = compute_complexity(file_path, imports)
        try:
            file_context = f"File: {file_path}\nImports: {', '.join(imports)}"
            if not primary_file_content:
                primary_file_content = file_context
            learning_objective = await generate_explanation(file_context, request.task_description)
        except Exception:
            learning_objective = f"Understand the role of {file_path} within the system."

        roadmap_steps.append(
            RoadmapStep(
                file_path=file_path,
                complexity_score=complexity_score,
                learning_objective=learning_objective
            )
        )

    roadmap_steps.sort(key=lambda s: {"Easy": 0, "Medium": 1, "Hard": 2}.get(s.complexity_score, 1))

    try:
        quiz = await generate_checkpoint_quiz(primary_file_content)
    except Exception:
        quiz = {"questions": []}

    return OnboardPayload(roadmap=roadmap_steps, quiz=quiz)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Compass AI"}