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
<<<<<<< HEAD
from engine.dependency_intelligence import build_dependency_intelligence
=======
from bob_core.context_service import ContextRetriever
from bob_core.prompts import build_mentor_prompt, classify_query
from bob_core.response_formatter import format_mentor_response, format_error_response, format_compass_response
from bob_core.orchestration import CompassOrchestrator
from bob_core.git_utils import clone_github_repo, cleanup_temp_repo, is_valid_github_url, GitCloneError
>>>>>>> fddb1bd4b432fd761f66db744cdeea688f89c7d2
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
    github_url: str
    task_description: Optional[str] = "Understand the codebase architecture"

<<<<<<< HEAD
=======
class CompassAnalysisRequest(BaseModel):
    github_url: str
    task_description: Optional[str] = "Understand the codebase architecture"
    max_roadmap_files: Optional[int] = 10
    include_tests: Optional[bool] = False
>>>>>>> fddb1bd4b432fd761f66db744cdeea688f89c7d2

class AskRequest(BaseModel):
    github_url: str
    question: str
    current_file: Optional[str] = None
    context: Optional[dict] = None


@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    # Validate GitHub URL
    if not is_valid_github_url(request.github_url):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GitHub URL: {request.github_url}"
        )
    
    temp_repo_path = None
    try:
<<<<<<< HEAD
        local_path, _ = resolve_repo_path(request.repo_path)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Repository resolution failed: {str(exc)}")

    try:
        intelligence = build_dependency_intelligence(local_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository intelligence failed: {str(exc)}")
=======
        # Clone the GitHub repository
        temp_repo_path, repo_name = clone_github_repo(request.github_url)
        
        # Parse the cloned repository
        repo_map = parse_repository(temp_repo_path)
    except GitCloneError as exc:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository parsing failed: {str(exc)}")
    finally:
        # Cleanup temporary directory
        if temp_repo_path:
            cleanup_temp_repo(temp_repo_path)
>>>>>>> fddb1bd4b432fd761f66db744cdeea688f89c7d2

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

<<<<<<< HEAD

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
=======
@app.post("/api/v1/compass/analyze")
async def analyze_repository_compass(request: CompassAnalysisRequest):
    """
    Complete Compass AI Analysis Endpoint
    
    This is the main endpoint that orchestrates the complete workflow:
    1. Clone GitHub repository to temporary directory
    2. Parse repository using engine/parser.py
    3. Calculate dependency intelligence using engine/dependency_intelligence.py
    4. Generate learning roadmap with Bob's AI explanations
    5. Create constellation graph for visualization
    6. Return formatted JSON for frontend
    7. Cleanup temporary directory
    
    Returns JSON structure:
    {
        "status": "success",
        "dependency_radius_score": 8.5,
        "learning_roadmap": [
            {
                "step": 1,
                "file_path": "src/config/database.js",
                "dependencies_count": 14,
                "priority": "critical",
                "bob_explanation": "...",
                "architectural_layer": "Database Layer",
                "complexity_score": 75,
                "dependency_radius": 2
            }
        ],
        "constellation_graph": {
            "nodes": [{"id": "...", "label": "...", "group": "..."}],
            "edges": [{"from": "...", "to": "...", "relationship": "imports"}]
        },
        "summary": {
            "total_files": 45,
            "total_dependencies": 120,
            "circular_dependencies": 2,
            "architectural_layers": {...},
            "foundational_files": [...],
            "hub_files": [...],
            "risky_files": [...]
        }
    }
    """
    # Validate GitHub URL
    if not is_valid_github_url(request.github_url):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GitHub URL: {request.github_url}"
        )
    
    temp_repo_path = None
    try:
        # Clone the GitHub repository
        temp_repo_path, repo_name = clone_github_repo(request.github_url)
        
        # Initialize orchestrator with cloned repo
        orchestrator = CompassOrchestrator(
            repo_path=temp_repo_path,
            include_tests=request.include_tests or False
        )
        
        # Run complete analysis
        result = await orchestrator.generate_complete_analysis(
            max_roadmap_files=request.max_roadmap_files or 10,
            task_description=request.task_description or "Understand the codebase architecture"
        )
        
        # Format response for frontend
        formatted_response = format_compass_response(result)
        
        return formatted_response
        
    except GitCloneError as gce:
        raise HTTPException(status_code=422, detail=f"Failed to clone repository: {str(gce)}")
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
>>>>>>> fddb1bd4b432fd761f66db744cdeea688f89c7d2
        )
    finally:
        # Always cleanup temporary directory
        if temp_repo_path:
            cleanup_temp_repo(temp_repo_path)

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
<<<<<<< HEAD
    return {"status": "ok", "service": "Compass AI"}
=======
    return {"status": "ok", "service": "Compass AI"}

@app.post("/api/v1/ask")
async def ask_mentor(request: AskRequest):
    """
    Interactive Q&A with IBM Bob mentor
    
    Provides context-aware answers about repository structure and code
    """
    # Validate GitHub URL
    if not is_valid_github_url(request.github_url):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GitHub URL: {request.github_url}"
        )
    
    # Determine query type early so we can use it in error responses
    query_type = classify_query(request.question)
    
    temp_repo_path = None
    try:
        # Clone the GitHub repository
        temp_repo_path, repo_name = clone_github_repo(request.github_url)
        
        # 1. Retrieve relevant context from cloned repo
        retriever = ContextRetriever(temp_repo_path)
        context = retriever.get_relevant_context(
            query=request.question,
            focus_file=request.current_file
        )
        
        # 2. Build enhanced prompt
        # Prepare context variables for prompt
        prompt_kwargs = {
            "file_path": request.current_file or "N/A",
            "imports": [],
            "imported_by": [],
            "complexity": "Unknown"
        }
        
        # Add focus file context if available
        if context.get("focus"):
            focus = context["focus"]
            prompt_kwargs.update({
                "file_path": focus.path,
                "imports": focus.imports,
                "imported_by": focus.imported_by,
                "complexity": focus.complexity
            })
        
        # Build the prompt
        prompt = build_mentor_prompt(
            query_type=query_type,
            repo_context={
                "name": repo_name,
                "files": retriever.repo_map.files if retriever.repo_map else {}
            },
            user_question=request.question,
            **prompt_kwargs
        )
        
        # 3. Call IBM Bob via existing service
        from bob_core.bob_service import build_payload, build_headers, WATSONX_GENERATE_URL
        import httpx
        
        payload = build_payload(prompt, max_tokens=500)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=build_headers(),
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            raw_response = results[0].get("generated_text", "I couldn't generate a response.") if results else "I couldn't generate a response."
        
        # 4. Format for UI
        formatted = format_mentor_response(
            raw_response=raw_response,
            context=context,
            query_type=query_type
        )
        
        return formatted
        
    except GitCloneError as gce:
        return format_error_response(f"Failed to clone repository: {str(gce)}", query_type=query_type)
    except HTTPException:
        raise
    except Exception as e:
        # Return formatted error response with correct query_type
        return format_error_response(str(e), query_type=query_type)
    finally:
        # Always cleanup temporary directory
        if temp_repo_path:
            cleanup_temp_repo(temp_repo_path)
>>>>>>> fddb1bd4b432fd761f66db744cdeea688f89c7d2
