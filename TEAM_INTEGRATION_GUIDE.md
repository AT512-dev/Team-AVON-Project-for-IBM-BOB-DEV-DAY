# Team Integration Guide - Quick Reference

## For Ali Jan (UI Developer)

### Base URL
```
http://localhost:8000
```

---

### Endpoint 1: Health Check

**URL:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "service": "Compass AI"
}
```

---

### Endpoint 2: Generate Roadmap

**URL:** `POST /api/v1/generate-roadmap`

**Request:**
```json
{
  "repo_path": "/absolute/path/to/repository",
  "task_description": "Understand authentication flow"
}
```

**Response:**
```json
{
  "roadmap": [
    {
      "file_path": "utils.py",
      "complexity_score": "Easy",
      "learning_objective": "Understand helper functions for data validation"
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

**JavaScript Example:**
```javascript
const generateRoadmap = async (repoPath, taskDescription) => {
  const response = await fetch('http://localhost:8000/api/v1/generate-roadmap', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repo_path: repoPath,
      task_description: taskDescription
    })
  });
  
  const data = await response.json();
  return data;
};

// Usage
const roadmap = await generateRoadmap('/path/to/repo', 'Learn authentication');
console.log(roadmap.roadmap); // Array of files to study
console.log(roadmap.quiz); // Quiz questions
```

---

### Endpoint 3: Ask Question (Main Interactive Endpoint)

**URL:** `POST /api/v1/ask`

**Request:**
```json
{
  "repo_path": "/absolute/path/to/repository",
  "question": "What does auth.py do?",
  "current_file": "services/auth.py",
  "context": {
    "task": "understanding authentication"
  }
}
```

**Fields:**
- `repo_path` (required): Absolute path to repository
- `question` (required): User's question
- `current_file` (optional): File currently being studied
- `context` (optional): Additional context object

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
- `answer`: Bob's response text (markdown supported)
- `cited_files`: Array of files mentioned with metadata
- `related_files`: Array of related file paths
- `next_steps`: Array of recommended actions
- `confidence`: Score from 0-1
- `query_type`: "file_purpose", "where_to_start", "impact_analysis", or "general"

**JavaScript Example:**
```javascript
const askBob = async (repoPath, question, currentFile = null) => {
  const response = await fetch('http://localhost:8000/api/v1/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repo_path: repoPath,
      question: question,
      current_file: currentFile
    })
  });
  
  const data = await response.json();
  return data;
};

// Usage
const answer = await askBob(
  '/path/to/repo',
  'What does auth.py do?',
  'services/auth.py'
);

console.log(answer.answer); // Bob's response
console.log(answer.cited_files); // Files mentioned
console.log(answer.next_steps); // What to do next
```

**React Component Example:**
```jsx
import { useState } from 'react';

function BobChat({ repoPath }) {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_path: repoPath,
          question: question
        })
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask Bob a question..."
      />
      <button onClick={askQuestion} disabled={loading}>
        {loading ? 'Asking...' : 'Ask'}
      </button>
      
      {response && (
        <div>
          <p>{response.answer}</p>
          <h4>Cited Files:</h4>
          <ul>
            {response.cited_files.map(file => (
              <li key={file.path}>
                {file.path} - {file.complexity}
              </li>
            ))}
          </ul>
          <h4>Next Steps:</h4>
          <ul>
            {response.next_steps.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

### Query Types

Bob automatically classifies questions into 4 types:

1. **file_purpose** - "What does X do?"
2. **where_to_start** - "Where should I start?"
3. **impact_analysis** - "What breaks if I change X?"
4. **general** - Other questions

---

### Error Handling

**Error Response Format:**
```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `422 Unprocessable Entity` - Invalid input
- `500 Internal Server Error` - Server error

---

## For Karl (Dependency Graph Service)

### What Bob Needs from You

Bob's dependency integration expects this data format for each file:

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

**Field Descriptions:**
- `file_path` (string): Relative path to file
- `complexity` (float 0-1): Complexity score (0=simple, 1=complex)
- `centrality` (float 0-1): How many files depend on it (0=isolated, 1=central)
- `distance_from_entry` (int): Hops from main entry point (0=entry point)
- `recommendation` (string): "start_here", "study_later", or "advanced"

### Integration Options

**Option 1: REST API (Recommended)**

Create an endpoint that Bob can call:

```
GET /api/scores/{file_path}
```

Response:
```json
{
  "file_path": "auth.py",
  "complexity": 0.65,
  "centrality": 0.82,
  "distance_from_entry": 2,
  "recommendation": "study_later"
}
```

**Option 2: Batch API**

```
POST /api/scores/batch
```

Request:
```json
{
  "files": ["auth.py", "models.py", "utils.py"]
}
```

Response:
```json
{
  "scores": [
    {
      "file_path": "auth.py",
      "complexity": 0.65,
      "centrality": 0.82,
      "distance_from_entry": 2,
      "recommendation": "study_later"
    },
    {
      "file_path": "models.py",
      "complexity": 0.3,
      "centrality": 0.9,
      "distance_from_entry": 1,
      "recommendation": "start_here"
    }
  ]
}
```

**Option 3: Shared Database/Cache**

Store scores in Redis or shared database that Bob can read.

### Integration Code (Bob's Side)

In `bob_core/dependency_integration.py`, update this method:

```python
def _fetch_from_karl_service(self, file_path: str) -> Optional[DependencyScore]:
    """Fetch from Karl's service"""
    try:
        # YOUR API URL HERE
        response = requests.get(f"{KARL_SERVICE_URL}/api/scores/{file_path}")
        if response.status_code == 200:
            data = response.json()
            return DependencyScore(
                file_path=file_path,
                complexity=data["complexity"],
                centrality=data["centrality"],
                distance_from_entry=data["distance_from_entry"],
                recommendation=data["recommendation"]
            )
    except Exception as e:
        print(f"Failed to fetch from Karl's service: {e}")
    return None
```

### How Bob Uses Your Scores

1. **Learning Path Recommendations**
   - Sorts files by: low complexity + high centrality = study first
   - Uses `distance_from_entry` to show architectural layers

2. **Complexity Labels**
   - 0-0.33: "Easy"
   - 0.33-0.67: "Medium"
   - 0.67-1.0: "Hard"

3. **File Prioritization**
   - High centrality files are shown as "important"
   - Entry points (distance=0) are highlighted
   - Recommendations guide learning order

---

## Testing

### Test with cURL

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate Roadmap:**
```bash
curl -X POST http://localhost:8000/api/v1/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "task_description": "Learn authentication"
  }'
```

**Ask Question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "question": "What does main.py do?"
  }'
```

---

## Quick Start

1. **Start Bob's Server:**
```bash
cd Team-AVON-Project-for-IBM-BOB-DEV-DAY
uvicorn bob_core.main:app --reload --port 8000
```

2. **Test Health:**
```bash
curl http://localhost:8000/health
```

3. **Ask a Question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo", "question": "Where should I start?"}'
```

---

## Contact

- **Harshal** - IBM Bob Integration
- **Ali Jan** - UI Development
- **Karl** - Dependency Graph Service

---

**Last Updated:** 2026-05-16  
**Version:** 1.0.0  
**Status:** Production Ready