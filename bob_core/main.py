from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import shutil
import os

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

_clone_cache: dict[str, str] = {}


def resolve_repo_path(repo_path: str) -> tuple[str, bool]:
    if repo_path.startswith("https://github.com") or repo_path.startswith("http://github.com"):
        if repo_path in _clone_cache:
            cached = _clone_cache[repo_path]
            if os.path.exists(cached):
                return cached, False
        tmp_dir = tempfile.mkdtemp(prefix="compass_clone_")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_path, tmp_dir],
                check=True,
                capture_output=True,
                timeout=60,
            )
            _clone_cache[repo_path] = tmp_dir
            return tmp_dir, True
        except subprocess.CalledProcessError as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise ValueError(f"Git clone failed: {e.stderr.decode()[:200]}")
        except subprocess.TimeoutExpired:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise ValueError("Git clone timed out after 60 seconds.")
        except FileNotFoundError:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise ValueError("git is not installed or not on PATH.")
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
    return repo_path, False


class OnboardRequest(BaseModel):
    repo_path: str
    task_description: Optional[str] = "Understand the codebase architecture"


class AskRequest(BaseModel):
    repo_path: str
    question: str
    current_file: Optional[str] = None
    context: Optional[dict] = None


@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    try:
        local_path, _ = resolve_repo_path(request.repo_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Repository resolution failed: {str(exc)}")

    try:
        intelligence = build_dependency_intelligence(local_path)
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
            learning_objective = await generate_explanation(
                file_context,
                request.task_description or "Understand the codebase architecture"
            )
        except Exception:
            learning_objective = item.learning_reason

        roadmap_steps.append(
            RoadmapStep(
                file_path=item.file,
                complexity_score=item.complexity_score,
                learning_objective=learning_objective,
            )
        )

    try:
        quiz = await generate_checkpoint_quiz(primary_file_content)
    except Exception:
        quiz = {"questions": []}

    return OnboardPayload(roadmap=roadmap_steps, quiz=quiz)


@app.post("/api/v1/ask")
async def ask_bob(request: AskRequest):
    try:
        local_path, _ = resolve_repo_path(request.repo_path)
    except ValueError as exc:
        from bob_core.response_formatter import format_error_response
        return format_error_response(str(exc), "general")

    try:
        from bob_core.context_service import ContextRetriever
        from bob_core.prompts import build_mentor_prompt, classify_query
        from bob_core.response_formatter import format_mentor_response, format_error_response

        retriever = ContextRetriever(local_path)
        query_type = classify_query(request.question)
        context = retriever.get_relevant_context(request.question, focus_file=request.current_file)

        repo_context = {
            "name": local_path.split(os.sep)[-1],
            "files": retriever.repo_map.files if retriever.repo_map else {},
        }

        focus = context.get("focus")
        prompt = build_mentor_prompt(
            query_type=query_type,
            repo_context=repo_context,
            user_question=request.question,
            file_path=request.current_file or "N/A",
            imports=focus.imports if focus else [],
            imported_by=focus.imported_by if focus else [],
            complexity=focus.complexity if focus else "Unknown",
            current_file=request.current_file or "N/A",
        )

        raw_answer = await generate_explanation(prompt, request.question)
        return format_mentor_response(raw_answer, context, query_type)

    except Exception as exc:
        from bob_core.response_formatter import format_error_response
        return format_error_response(str(exc), "general")


@app.post("/api/v1/dependency-intelligence", response_model=DependencyIntelligencePayload)
async def dependency_intelligence(request: IntelligenceRequest):
    try:
        local_path, _ = resolve_repo_path(request.repo_path)
        return build_dependency_intelligence(local_path, include_tests=bool(request.include_tests))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Dependency intelligence failed: {str(exc)}")


@app.get("/api/v1/repo-map")
async def repo_map(repo_path: str):
    try:
        local_path, _ = resolve_repo_path(repo_path)
        return parse_repository(local_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository parsing failed: {str(exc)}")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Compass AI"}