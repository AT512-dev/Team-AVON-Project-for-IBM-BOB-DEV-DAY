from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any, List, Dict
import os
import shutil
import hashlib
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from git import Repo

load_dotenv()

from bob_core.schemas import DependencyIntelligencePayload, IntelligenceRequest, OnboardPayload, RoadmapStep
from bob_core.bob_service import generate_explanation, generate_checkpoint_quiz, answer_question
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

WORKSPACE_DIR = os.path.join(os.getcwd(), "compass_workspaces")
os.makedirs(WORKSPACE_DIR, exist_ok=True)


def resolve_and_clone_repo(path_or_url: str) -> str:
    stripped_path = path_or_url.strip()

    if stripped_path.startswith("http://") or stripped_path.startswith("https://"):
        url_hash = hashlib.md5(stripped_path.encode("utf-8")).hexdigest()[:12]
        repo_name = stripped_path.split("/")[-1].replace(".git", "")
        local_target_path = os.path.join(WORKSPACE_DIR, f"{repo_name}_{url_hash}")

        if os.path.exists(local_target_path) and os.listdir(local_target_path):
            print(f"📦 Workspace Cache Hit: Utilizing existing directory path: {local_target_path}")
            return local_target_path

        print(f"📥 Remote Git URL Detected. Initializing fresh workspace clone to: {local_target_path}")
        try:
            if os.path.exists(local_target_path):
                shutil.rmtree(local_target_path)
            Repo.clone_from(stripped_path, local_target_path, depth=1)
            return local_target_path
        except Exception as clone_err:
            raise RuntimeError(f"Failed to clone repository: {str(clone_err)}")

    if not os.path.exists(stripped_path):
        raise FileNotFoundError(f"Repository path does not exist: {stripped_path}")

    return stripped_path


# ── Shared validator mixin ────────────────────────────────────────────────────

def _normalise_repo(data: Any) -> Any:
    if isinstance(data, dict):
        if not data.get("repo_path") and data.get("repo_url"):
            data["repo_path"] = data["repo_url"]
        elif not data.get("repo_url") and data.get("repo_path"):
            data["repo_url"] = data["repo_path"]
    return data


# ── Request / Response models ─────────────────────────────────────────────────

class OnboardRequest(BaseModel):
    repo_path: Optional[str] = Field(default=None, alias="repo_url")
    task_description: Optional[str] = "Understand the codebase architecture"
    module: Optional[str] = None
    folder_filter: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_path_or_url(cls, data: Any) -> Any:
        return _normalise_repo(data)


class FileContentRequest(BaseModel):
    repo_path: Optional[str] = Field(default=None)
    repo_url: Optional[str] = Field(default=None)
    file_path: str

    @model_validator(mode="before")
    @classmethod
    def normalise_repo(cls, data: Any) -> Any:
        return _normalise_repo(data)


class AskRequest(BaseModel):
    repo_path: Optional[str] = Field(default=None)
    repo_url: Optional[str] = Field(default=None)
    question: str
    current_file: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def normalise_repo(cls, data: Any) -> Any:
        return _normalise_repo(data)


class CitedFile(BaseModel):
    path: str
    reason: str
    complexity: str
    loc: int = 0


class AskResponse(BaseModel):
    answer: str
    cited_files: List[CitedFile] = []
    related_files: List[str] = []
    next_steps: List[str] = []
    confidence: float = 0.9
    query_type: str = "general"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Compass AI"}


@app.post("/api/v1/generate-roadmap", response_model=OnboardPayload)
async def generate_roadmap(request: OnboardRequest):
    target_input = request.repo_path
    if not target_input:
        raise HTTPException(status_code=422, detail="Missing parameter: repo_path or repo_url is required.")

    try:
        local_workspace_path = resolve_and_clone_repo(target_input)
        intelligence = build_dependency_intelligence(local_workspace_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repository intelligence failed: {str(exc)}")

    roadmap_steps = []
    primary_file_content = ""

    folder_filter = (request.folder_filter or request.module or "").lower().strip()

    items_to_process = intelligence.roadmap
    if folder_filter:
        filtered = [i for i in intelligence.roadmap if folder_filter in i.file.lower()]
        if filtered:
            items_to_process = filtered
            print(f"🔍 folder_filter='{folder_filter}': {len(filtered)}/{len(intelligence.roadmap)} files")

    for item in items_to_process:
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


@app.post("/api/v1/ask", response_model=AskResponse)
async def ask_bob(request: AskRequest):
    """
    Chat endpoint — Bob answers questions about the codebase using
    the dependency intelligence graph + WatsonX explanation engine.
    """
    repo_input = request.repo_path or request.repo_url
    if not repo_input:
        raise HTTPException(status_code=422, detail="Missing repo_path or repo_url")

    try:
        local_workspace = resolve_and_clone_repo(repo_input)
        intelligence = build_dependency_intelligence(local_workspace)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Repo resolution failed: {str(exc)}")

    question = request.question.strip()
    q_lower = question.lower()

    roadmap = intelligence.roadmap or []

    if request.current_file:
        cf = request.current_file.lower()
        roadmap = sorted(roadmap, key=lambda i: (0 if cf in i.file.lower() else 1))

    if any(k in q_lower for k in ["complex", "risky", "hard", "difficult"]):
        roadmap = sorted(roadmap, key=lambda i: i.dependency_radius, reverse=True)

    top_items = roadmap[:5]

    combined_context = "\n\n".join(
        f"File: {item.file}\n"
        f"Layer: {item.architectural_layer}\n"
        f"Complexity: {item.complexity_score}\n"
        f"Dependencies: {', '.join(item.prerequisites[:3])}"
        for item in top_items
    )

    try:
        answer = await answer_question(combined_context, question)
    except Exception:
        answer = "Sorry, I encountered an issue processing your question against the codebase."

    cited_files = [
        CitedFile(
            path=item.file,
            reason=f"Identified within the structural {item.architectural_layer}.",
            complexity=str(item.complexity_score)
        )
        for item in top_items
    ]

    related_files = [item.file for item in roadmap[5:10]]

    next_steps = [
        "Review the target code architectures listed in your cited files.",
        "Verify edge-case handling across complex logic layers."
    ]

    return AskResponse(
        answer=answer,
        cited_files=cited_files,
        related_files=related_files,
        next_steps=next_steps,
        confidence=0.95 if top_items else 0.50,
        query_type="architecture" if "architecture" in q_lower else "general"
    )


@app.post("/api/v1/file-content")
async def get_file_content(request: FileContentRequest):
    """
    Retrieves the actual code contents of a specific file from the workspace.
    """
    repo_input = request.repo_path or request.repo_url
    if not repo_input:
        raise HTTPException(status_code=422, detail="Missing repo_path or repo_url")

    try:
        local_workspace = resolve_and_clone_repo(repo_input)
        safe_base = os.path.realpath(local_workspace)
        target_path = os.path.realpath(os.path.join(safe_base, request.file_path.lstrip("/")))
        
        if not target_path.startswith(safe_base):
            raise HTTPException(status_code=403, detail="Access denied: Directory traversal blocked.")
            
        if not os.path.exists(target_path) or os.path.isdir(target_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return {"file_path": request.file_path, "content": content}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to read file content: {str(exc)}")
