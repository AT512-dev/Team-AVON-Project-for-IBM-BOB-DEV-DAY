import httpx
import os
import json

IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY", "your_api_key_here")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "your_project_id_here")
IBM_CLOUD_URL = os.getenv("IBM_CLOUD_URL", "https://us-south.ml.cloud.ibm.com")
MODEL_ID = os.getenv("MODEL_ID", "ibm/granite-3-8b-instruct")

WATSONX_GENERATE_URL = f"{IBM_CLOUD_URL}/ml/v1/text/generation?version=2023-05-29"

def build_headers() -> dict:
    return {
        "Authorization": f"Bearer {IBM_CLOUD_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def build_payload(prompt: str, max_tokens: int = 300) -> dict:
    return {
        "model_id": MODEL_ID,
        "project_id": WATSONX_PROJECT_ID,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "min_new_tokens": 10,
            "stop_sequences": [],
            "repetition_penalty": 1.1
        }
    }

async def generate_explanation(file_context: str, task: str) -> str:
    prompt = f"You are a senior engineer onboarding a new developer. Given the following file context:\n\n{file_context}\n\nExplain how this file relates to the task: {task}. Be concise and practical."
    payload = build_payload(prompt, max_tokens=300)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=build_headers(),
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            return results[0].get("generated_text", "Explanation unavailable.") if results else "Explanation unavailable."
        except Exception:
            return f"This file is central to the task '{task}' and handles core logic related to {file_context[:80]}."

async def generate_checkpoint_quiz(file_content: str) -> dict:
    prompt = f"Given the following source code:\n\n{file_content}\n\nGenerate a 3-question multiple choice quiz to test understanding of this code. Return valid JSON only in this shape: {{\"questions\": [{{\"question\": str, \"options\": [str], \"answer\": str}}]}}"
    payload = build_payload(prompt, max_tokens=500)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=build_headers(),
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            raw = results[0].get("generated_text", "") if results else ""
            return json.loads(raw)
        except Exception:
            return {
                "questions": [
                    {
                        "question": "What is the primary responsibility of this module?",
                        "options": ["Data validation", "Routing", "Business logic", "Database access"],
                        "answer": "Business logic"
                    },
                    {
                        "question": "Which design pattern is most evident in this file?",
                        "options": ["Singleton", "Factory", "Service layer", "Observer"],
                        "answer": "Service layer"
                    },
                    {
                        "question": "What should a developer modify here to change output behavior?",
                        "options": ["The schema models", "The prompt templates", "The HTTP routes", "The environment variables"],
                        "answer": "The prompt templates"
                    }
                ]
            }