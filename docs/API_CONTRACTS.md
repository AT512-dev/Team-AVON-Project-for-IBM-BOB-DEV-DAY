# API Contracts - Compass AI

## Overview

This document defines the API contracts for the Compass AI IBM Bob Mentor System. These contracts are designed for integration with Ali Jan's UI and Karl's dependency graph service.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the service is running

**Request:** None

**Response:**
```json
{
  "status": "ok",
  "service": "Compass AI"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Generate Roadmap

**Endpoint:** `POST /api/v1/generate-roadmap`

**Description:** Generate a learning roadmap for a repository

**Request Body:**
```json
{
  "repo_path": "/path/to/repository",
  "task_description": "Understand authentication flow"
}
```

**Request Fields:**
- `repo_path` (string, required): Absolute path to the repository
- `task_description` (string, optional): Learning objective. Default: "Understand the codebase architecture"

**Response:**
```json
{
  "roadmap": [
    {
      "file_path": "utils.py",
      "complexity_score": "Easy",
      "learning_objective": "Understand helper functions for data validation and formatting"
    },
    {
      "file_path": "models.py",
      "complexity_score": "Medium",
      "learning_objective": "Study the User and Session data models"
    },
    {
      "file_path": "services/auth.py",
      "complexity_score": "Hard",
      "learning_objective": "Understand authentication logic and session management"
    }
  ],
  "quiz": {
    "questions": [
      {
        "question": "What is the primary responsibility of utils.py?",
        "options": ["Data validation", "Routing", "Business logic", "Database access"],
        "answer": "Data validation"
      }
    ]
  }
}
```

**Response Fields:**
- `roadmap` (array): Ordered list of files to study
  - `file_path` (string): Relative path to file
  - `complexity_score` (string): "Easy", "Medium", or "Hard"
  - `learning_objective` (string): What to learn from this file
- `quiz` (object): Checkpoint quiz
  - `questions` (array): Multiple choice questions

**Status Codes:**
- `200 OK` - Roadmap generated successfully
- `422 Unprocessable Entity` - Invalid repository path or parsing failed

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/home/user/my-project",
    "task_description": "Learn the authentication system"
  }'
```

---

### 3. Ask Question (Interactive Q&A)

**Endpoint:** `POST /api/v1/ask`

**Description:** Ask IBM Bob a question about the codebase

**Request Body:**
```json
{
  "repo_path": "/path/to/repository",
  "question": "What does auth.py do?",
  "current_file": "services/auth.py",
  "context": {
    "task": "understanding authentication"
  }
}
```

**Request Fields:**
- `repo_path` (string, required): Absolute path to the repository
- `question` (string, required): User's question
- `current_file` (string, optional): File currently being studied
- `context` (object, optional): Additional context for the question

**Response:**
```json
{
  "answer": "The `auth.py` file handles user authentication and session management. It imports `models.py` for the User schema and `utils.py` for token generation. This file is used by `main.py` and `router.py` to protect routes. Start by understanding the User model in `models.py` first.",
  "cited_files": [
    {
      "path": "services/auth.py",
      "reason": "Primary file in question",
      "complexity": "Medium",
      "loc": 150
    },
    {
      "path": "models.py",
      "reason": "Imported for User model",
      "complexity": "Easy",
      "loc": 80
    },
    {
      "path": "utils.py",
      "reason": "Token generation helpers",
      "complexity": "Easy",
      "loc": 45
    }
  ],
  "related_files": ["main.py", "router.py", "database.py"],
  "next_steps": [
    "Study models.py to understand the User schema",
    "Check utils.py for token generation functions",
    "Review how main.py uses auth.py for route protection"
  ],
  "confidence": 0.85,
  "query_type": "file_purpose"
}
```

**Response Fields:**
- `answer` (string): Bob's response to the question
- `cited_files` (array): Files mentioned in the response
  - `path` (string): File path
  - `reason` (string): Why this file is relevant
  - `complexity` (string): "Easy", "Medium", or "Hard"
  - `loc` (number): Lines of code
- `related_files` (array): Other relevant files
- `next_steps` (array): Recommended actions
- `confidence` (number): Confidence score (0-1)
- `query_type` (string): Type of query ("file_purpose", "where_to_start", "impact_analysis", "general")

**Query Types:**

1. **file_purpose** - Questions about what a file does
   - Examples: "What does auth.py do?", "What is the purpose of models.py?"

2. **where_to_start** - Questions about learning order
   - Examples: "Where should I start?", "What file should I begin with?"

3. **impact_analysis** - Questions about changes and dependencies
   - Examples: "What breaks if I modify this?", "What depends on auth.py?"

4. **general** - Other questions
   - Examples: "How does authentication work?", "Explain the architecture"

**Status Codes:**
- `200 OK` - Question answered successfully
- `422 Unprocessable Entity` - Invalid request
- `500 Internal Server Error` - Processing error (returns formatted error response)

**Error Response:**
```json
{
  "answer": "I encountered an issue processing your question: [error details]. Please try rephrasing your question or check the repository path.",
  "cited_files": [],
  "related_files": [],
  "next_steps": [
    "Verify the repository path is correct",
    "Try asking a more specific question",
    "Check if the file exists in the repository"
  ],
  "confidence": 0.0,
  "query_type": "general",
  "error": true
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/home/user/my-project",
    "question": "What does auth.py do?",
    "current_file": "services/auth.py"
  }'
```

---

## Integration with Karl's Dependency Service

### Expected Data Format from Karl

Bob's context service can integrate with Karl's dependency graph service to enhance recommendations.

**Expected Format:**
```json
{
  "file_path": "services/auth.py",
  "complexity": 0.65,
  "centrality": 0.82,
  "distance_from_entry": 2,
  "recommendation": "study_later"
}
```

**Fields:**
- `file_path` (string): File path
- `complexity` (number): Complexity score (0-1 scale)
- `centrality` (number): How many files depend on it (0-1 scale)
- `distance_from_entry` (number): Hops from main entry point
- `recommendation` (string): "start_here", "study_later", or "advanced"

**Integration Point:**

The `DependencyScoreProvider` class in `bob_core/dependency_integration.py` provides the interface:

```python
from bob_core.dependency_integration import DependencyScoreProvider

# Initialize with mock data (for testing)
provider = DependencyScoreProvider(use_mock=True)

# Get score for a file
score = provider.get_file_score("auth.py")

# Get learning path for multiple files
learning_path = provider.get_learning_path(["auth.py", "models.py", "utils.py"])
```

**To integrate Karl's real service:**

1. Set `use_mock=False` in `DependencyScoreProvider`
2. Implement `_fetch_from_karl_service()` method with actual API call
3. Configure Karl's service URL in environment variables

---

## Integration with Ali Jan's UI

### Recommended UI Flow

1. **Initial Load:**
   ```
   POST /api/v1/generate-roadmap
   → Display roadmap with complexity indicators
   → Show checkpoint quiz
   ```

2. **User Clicks on File:**
   ```
   POST /api/v1/ask
   question: "What does [filename] do?"
   current_file: [filename]
   → Display answer with cited files
   → Show next steps
   ```

3. **User Asks Follow-up:**
   ```
   POST /api/v1/ask
   question: [user's question]
   current_file: [current file]
   → Display contextual answer
   ```

### UI Components Needed

1. **Roadmap View**
   - File list with complexity badges
   - Progress tracking
   - Quiz modal

2. **Chat Interface**
   - Question input
   - Answer display with markdown support
   - Cited files as clickable links
   - Next steps as action items

3. **File Context Panel**
   - Current file highlight
   - Related files list
   - Dependency visualization

---

## Rate Limits

Currently no rate limits are enforced. Recommended limits for production:

- `/health`: Unlimited
- `/api/v1/generate-roadmap`: 10 requests/minute per IP
- `/api/v1/ask`: 30 requests/minute per IP

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "detail": "Error description"
}
```

Common errors:
- `422 Unprocessable Entity`: Invalid input
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: WatsonX API unavailable

---

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| `/health` | < 10ms | Simple status check |
| `/generate-roadmap` | < 5s | Includes parsing + AI generation |
| `/ask` (with cache) | < 2s | Context retrieval cached |
| `/ask` (no cache) | < 6s | Includes parsing + AI call |

---

## Authentication

Currently no authentication is required. For production:

1. Add API key authentication
2. Use JWT tokens for user sessions
3. Implement OAuth for GitHub integration

---

## Versioning

Current version: `v1`

API versioning is included in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.

---

## Support

For issues or questions:
- GitHub Issues: [repository URL]
- Team Contact: Harshal (IBM Bob Integration)
- Dependencies: Karl (Dependency Graph), Ali Jan (UI)

---

**Last Updated:** 2026-05-16  
**Version:** 1.0.0  
**Status:** Phase 3 Complete