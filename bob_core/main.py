from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

from bob_core.schemas import OnboardPayload, RoadmapStep
from bob_core.bob_service import generate_explanation, generate_checkpoint_quiz
from bob_core.context_service import ContextRetriever
from bob_core.prompts import build_mentor_prompt, classify_query
from bob_core.response_formatter import format_mentor_response, format_error_response
from engine.parser import parse_repository
from engine.metrics import compute_complexity

app = FastAPI(title="Compass AI", version="1.0.0")

class OnboardRequest(BaseModel):
    repo_path: str
    task_description: Optional[str] = "Understand the codebase architecture"

class AskRequest(BaseModel):
    repo_path: str
    question: str
    current_file: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

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
            task_desc = request.task_description or "Understand the codebase architecture"
            learning_objective = await generate_explanation(file_context, task_desc)
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

@app.post("/api/v1/ask")
async def ask_mentor(request: AskRequest):
    """
    Interactive Q&A with IBM Bob mentor
    
    Provides context-aware answers about repository structure and code
    """
    # Determine query type early so we can use it in error responses
    query_type = classify_query(request.question)
    
    try:
        # 1. Retrieve relevant context
        retriever = ContextRetriever(request.repo_path)
        context = retriever.get_relevant_context(
            query=request.question,
            focus_file=request.current_file
        )
        
        # 2. Build enhanced prompt
        repo_name = os.path.basename(request.repo_path)
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        # Return formatted error response with correct query_type
        return format_error_response(str(e), query_type=query_type)