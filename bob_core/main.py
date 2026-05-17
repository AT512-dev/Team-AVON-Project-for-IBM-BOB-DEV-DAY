import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from bob_core.bob_service import generate_checkpoint_quiz, generate_explanation
from bob_core.context_service import ContextRetriever
from bob_core.git_utils import GitCloneError, cleanup_temp_repo, clone_github_repo, is_valid_github_url
from bob_core.orchestration import CompassOrchestrator
from bob_core.prompts import build_mentor_prompt, classify_query
from bob_core.response_formatter import format_compass_response, format_error_response, format_mentor_response
from bob_core.schemas import DependencyIntelligencePayload, IntelligenceRequest, OnboardPayload, RoadmapStep
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


class RepositoryRequest(BaseModel):
    repo_path: Optional[str] = None
    github_url: Optional[str] = None


class OnboardRequest(RepositoryRequest):
    task_description: Optional[str] = "Understand the codebase architecture"


class CompassAnalysisRequest(RepositoryRequest):
    task_description: Optional[str] = "Understand the codebase architecture"
    max_roadmap_files: Optional[int] = 10
    include_tests: Optional[bool] = False


class AskRequest(RepositoryRequest):
    question: str
    current_file: Optional[str] = None
    context: Optional[dict[str, Any]] = None


def request_repository_value(request: RepositoryRequest) -> str:
    value = request.github_url or request.repo_path
    if not value:
        raise ValueError("Either github_url or repo_path is required.")
    return value


def resolve_repo_path(repo_value: str) -> tuple[str, bool]:
    """
    Resolve either a local repository path or a GitHub URL.

    Returns (local_path, should_cleanup). GitHub URLs are cloned to a temporary
    directory and must be cleaned up by the caller.
    """
    if is_valid_github_url(repo_value):
        local_path, _repo_name = clone_github_repo(repo_value)
        return local_path, True
    return repo_value, False


@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    local_path: Optional[str] = None
    should_cleanup = False

    try:
        local_path, should_cleanup = resolve_repo_path(request_repository_value(request))
        intelligence = build_dependency_intelligence(local_path)
    except GitCloneError as exc:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository intelligence failed: {str(exc)}")
    finally:
        if should_cleanup and local_path:
            cleanup_temp_repo(local_path)

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
                request.task_description or "Understand the codebase architecture",
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


@app.post("/api/v1/compass/analyze")
async def analyze_repository_compass(request: CompassAnalysisRequest):
    local_path: Optional[str] = None
    should_cleanup = False

    try:
        local_path, should_cleanup = resolve_repo_path(request_repository_value(request))
        orchestrator = CompassOrchestrator(
            repo_path=local_path,
            include_tests=bool(request.include_tests),
        )
        result = await orchestrator.generate_complete_analysis(
            max_roadmap_files=request.max_roadmap_files or 10,
            task_description=request.task_description or "Understand the codebase architecture",
        )
        return format_compass_response(result)
    except GitCloneError as exc:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}")
    finally:
        if should_cleanup and local_path:
            cleanup_temp_repo(local_path)


@app.post("/api/v1/ask")
async def ask_mentor(request: AskRequest):
    query_type = classify_query(request.question)
    local_path: Optional[str] = None
    should_cleanup = False

    try:
        local_path, should_cleanup = resolve_repo_path(request_repository_value(request))
        retriever = ContextRetriever(local_path)
        context = retriever.get_relevant_context(
            query=request.question,
            focus_file=request.current_file,
        )

        prompt_kwargs = {
            "file_path": request.current_file or "N/A",
            "imports": [],
            "imported_by": [],
            "complexity": "Unknown",
        }
        if context.get("focus"):
            focus = context["focus"]
            prompt_kwargs.update(
                {
                    "file_path": focus.path,
                    "imports": focus.imports,
                    "imported_by": focus.imported_by,
                    "complexity": focus.complexity,
                }
            )

        prompt = build_mentor_prompt(
            query_type=query_type,
            repo_context={
                "name": os.path.basename(local_path),
                "files": retriever.repo_map.files if retriever.repo_map else {},
            },
            user_question=request.question,
            **prompt_kwargs,
        )

        raw_response = await generate_explanation(prompt, request.question)
        return format_mentor_response(raw_response, context, query_type)
    except HTTPException:
        raise
    except Exception as exc:
        return format_error_response(str(exc), query_type=query_type)
    finally:
        if should_cleanup and local_path:
            cleanup_temp_repo(local_path)


@app.post("/api/v1/dependency-intelligence", response_model=DependencyIntelligencePayload)
async def dependency_intelligence(request: IntelligenceRequest):
    local_path: Optional[str] = None
    should_cleanup = False

    try:
        local_path, should_cleanup = resolve_repo_path(request.repo_path)
        return build_dependency_intelligence(local_path, include_tests=bool(request.include_tests))
    except GitCloneError as exc:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Dependency intelligence failed: {str(exc)}")
    finally:
        if should_cleanup and local_path:
            cleanup_temp_repo(local_path)


@app.get("/api/v1/repo-map")
async def repo_map(repo_path: str):
    local_path: Optional[str] = None
    should_cleanup = False

    try:
        local_path, should_cleanup = resolve_repo_path(repo_path)
        return parse_repository(local_path)
    except GitCloneError as exc:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository parsing failed: {str(exc)}")
    finally:
        if should_cleanup and local_path:
            cleanup_temp_repo(local_path)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Compass AI"}
