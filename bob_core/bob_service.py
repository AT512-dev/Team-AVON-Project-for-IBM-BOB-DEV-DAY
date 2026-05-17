import httpx
import os
import json
import time

# Configurations
IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY", "3nXkb3MFGDBHkMerFBf-a5-0i7oTRLREXC42cxufaEWM")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "385958db-ea1e-41ef-8873-b25f75f9f51f")
IBM_CLOUD_URL = os.getenv("IBM_CLOUD_URL", "https://us-south.ml.cloud.ibm.com")
MODEL_ID = os.getenv("MODEL_ID", "ibm/granite-3-8b-instruct")

WATSONX_GENERATE_URL = f"{IBM_CLOUD_URL}/ml/v1/text/generation?version=2023-05-29"
IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

# Simple token cache variables
_cached_token = None
_token_expiry = 0

async def get_iam_token() -> str:
    """Exchanges the raw IBM Cloud API key for a valid IAM Access Token."""
    global _cached_token, _token_expiry
    
    # Return cached token if it's still valid (with a 60-second buffer)
    if _cached_token and time.time() < (_token_expiry - 60):
        return _cached_token

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                IAM_TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": IBM_CLOUD_API_KEY
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            _cached_token = data["access_token"]
            # 'expires_in' is usually 3600 seconds
            _token_expiry = time.time() + data.get("expires_in", 3600)
            return _cached_token
        except Exception as e:
            raise RuntimeError(f"Failed to generate IBM IAM Token: {str(e)}")

async def build_headers() -> dict:
    """Builds headers using a valid IAM Bearer token."""
    token = await get_iam_token()
    return {
        "Authorization": f"Bearer {token}",
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

# Inside bob_core/bob_service.py

async def answer_question(file_context: str, question: str) -> str:
    """Dedicated function to answer user questions based on file context."""
    prompt = (
        f"You are an expert AI assistant. Answer the user's question accurately using only "
        f"the provided file context. Be conversational, direct, and concise.\n\n"
        f"File Context:\n{file_context}\n\n"
        f"User Question: {question}\n\n"
        f"Answer:"
    )
    payload = build_payload(prompt, max_tokens=500)
    async with httpx.AsyncClient() as client:
        try:
            headers = await build_headers()
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=headers,
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # FIX: Index into the first element of the list instead of using .get()
            if results and isinstance(results, list):
                return results[0].get("generated_text", "Unable to answer.")
            return "Unable to answer."
        except Exception as e:
            # Helpful print statement for terminal debugging
            print(f"❌ WatsonX API Call Failed: {str(e)}")
            return "Sorry, I encountered an issue processing your question against the codebase."

    """Dedicated function to answer user questions based on file context."""
    prompt = (
        f"You are an expert AI assistant. Answer the user's question accurately using only "
        f"the provided file context. Be conversational, direct, and concise.\n\n"
        f"File Context:\n{file_context}\n\n"
        f"User Question: {question}\n\n"
        f"Answer:"
    )
    payload = build_payload(prompt, max_tokens=500)
    async with httpx.AsyncClient() as client:
        try:
            headers = await build_headers()
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=headers,
                timeout=15.0
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            return results[0].get("generated_text", "Unable to answer.") if results else "Unable to answer."
        except Exception:
            return "Sorry, I encountered an issue processing your question against the codebase."

async def generate_explanation(file_context: str, task: str) -> str:
    prompt = f"You are a senior engineer onboarding a new developer. Given the following file context:\n\n{file_context}\n\nExplain how this file relates to the task: {task}. Be concise and practical."
    payload = build_payload(prompt, max_tokens=300)
    async with httpx.AsyncClient() as client:
        try:
            headers = await build_headers()
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=headers,
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
            headers = await build_headers()
            response = await client.post(
                WATSONX_GENERATE_URL,
                json=payload,
                headers=headers,
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
