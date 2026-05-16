# CONTEXT.md — Compass AI

## Project Overview

**Compass AI** is a developer onboarding tool that transforms GitHub repositories into interactive guided roadmaps. Instead of spending weeks deciphering a codebase, new engineers ask questions and receive contextual, file-aware answers — like having a senior developer available 24/7.

**IBM Bob (WatsonX)** is the intelligence core that powers the mentoring experience.

---

## Domain Terms

| Term | Meaning |
|------|---------|
| **Mentor Prompt** | System instruction that makes IBM Bob respond like a senior engineer, not a generic chatbot. Includes repository context and relationship awareness. |
| **Context Window** | The file content + dependency information + complexity scores fed to Bob per query. Limited by token constraints. |
| **Dependency Radius** | Karl's metric combining complexity score + architectural distance from entry points. Determines learning order. |
| **Chunking Strategy** | How we split large files (>500 LOC) into digestible semantic pieces for Bob's context window. |
| **Grounding Context** | Repository structure + file relationships + import graph that Bob reasons over to provide accurate answers. |
| **Interactive Loop** | The cycle: User Question → Context Retrieval → Bob Response → UI Display → Next Question |
| **File-Aware Response** | Bob's answer that cites specific files (e.g., `auth.py`) and explains relationships between components. |
| **Relationship Mapping** | Bidirectional dependency graph: which files import what AND which files are imported by what. |
| **Roadmap Step** | A single learning checkpoint in the onboarding journey, tied to a specific file with complexity score. |
| **Learning Objective** | Bob-generated explanation of what a developer should understand after studying a particular file. |
| **Checkpoint Quiz** | Auto-generated multiple-choice questions to verify understanding before moving to next roadmap step. |
| **Query Classification** | Categorizing user questions into types: file_purpose, where_to_start, impact_analysis, or general. |
| **Semantic Chunking** | Splitting code by logical boundaries (classes, functions) rather than arbitrary line counts. |
| **Reverse Dependencies** | Files that depend on a given file (who imports me?). Critical for impact analysis. |
| **Entry Point** | Main files where execution begins (e.g., `main.py`, `app.py`). Starting point for dependency distance calculation. |

---

## Architecture

**Three-Tier System:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Ali Jan's UI Layer                       │
│  (React/Vue - sends questions, displays roadmaps & answers)  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Bob Core)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /generate- │  │     /ask     │  │   /health    │      │
│  │    roadmap   │  │   endpoint   │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                 │
│         ▼                  ▼                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Context Retrieval Service                 │       │
│  │  - Fetch relevant files                          │       │
│  │  - Build dependency graph                        │       │
│  │  - Apply chunking for large files                │       │
│  │  - Inject Karl's complexity scores               │       │
│  └──────────────────┬───────────────────────────────┘       │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │           Prompt Builder                          │       │
│  │  - Select appropriate template                   │       │
│  │  - Inject repository context                     │       │
│  │  - Format for WatsonX API                        │       │
│  └──────────────────┬───────────────────────────────┘       │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              IBM WatsonX (IBM Bob)                           │
│  - Granite 3 8B Instruct model                              │
│  - Generates mentor-like responses                          │
│  - Returns structured explanations                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Response Formatter                            │
│  - Parse Bob's raw text                                     │
│  - Extract cited files                                      │
│  - Structure as JSON for UI                                 │
│  - Add confidence scores                                    │
└─────────────────────────────────────────────────────────────┘
```

**Supporting Services:**

```
┌──────────────────────┐     ┌──────────────────────┐
│   Repository Parser  │     │  Dependency Graph    │
│   (engine/parser.py) │     │  (Karl's Service)    │
│                      │     │                      │
│  - Walk file tree    │     │  - Complexity scores │
│  - Extract imports   │     │  - Centrality ranks  │
│  - Build repo map    │     │  - Learning paths    │
└──────────────────────┘     └──────────────────────┘
```

---

## Component Responsibilities

### Harshal's Domain (IBM Bob Orchestration)

1. **Prompt Engineering** (`bob_core/prompts.py`)
   - Design mentor persona
   - Create query-specific templates
   - Inject repository context

2. **Context Retrieval** (`bob_core/context_service.py`)
   - Fetch relevant files per query
   - Build bidirectional dependency graph
   - Cache repository structure

3. **Interactive Q&A** (`bob_core/main.py` - `/ask` endpoint)
   - Route questions to Bob with context
   - Format responses for UI
   - Handle error cases

4. **Chunking Strategy** (`bob_core/chunking.py`)
   - Split large files semantically
   - Select relevant chunks per query
   - Manage context window limits

5. **Integration Layer** (`bob_core/dependency_integration.py`)
   - Consume Karl's dependency scores
   - Feed scores into Bob's context
   - Influence learning path recommendations

### Karl's Domain (Dependency Graph)

- Compute complexity scores per file
- Calculate architectural distance from entry points
- Rank files by importance (centrality)
- Provide learning path recommendations

### Ali Jan's Domain (UI)

- Display interactive roadmap
- Send user questions to `/ask` endpoint
- Render Bob's responses with cited files
- Show checkpoint quizzes

---

## Data Flow Examples

### Example 1: Generate Roadmap

```
1. UI sends: POST /api/v1/generate-roadmap
   {
     "repo_path": "/path/to/repo",
     "task_description": "Understand authentication flow"
   }

2. Backend:
   - Parses repository → gets file tree + imports
   - Computes complexity per file
   - Calls Bob to generate learning objectives
   - Sorts files by complexity (Easy → Hard)
   - Generates checkpoint quiz

3. Returns:
   {
     "roadmap": [
       {
         "file_path": "utils.py",
         "complexity_score": "Easy",
         "learning_objective": "Understand helper functions..."
       },
       ...
     ],
     "quiz": { "questions": [...] }
   }
```

### Example 2: Ask Question

```
1. UI sends: POST /api/v1/ask
   {
     "repo_path": "/path/to/repo",
     "question": "What does auth.py do?",
     "current_file": "services/auth.py"
   }

2. Backend:
   - Retrieves context for auth.py
   - Gets imports: ["models.py", "utils.py"]
   - Gets imported_by: ["main.py", "router.py"]
   - Gets complexity: "Medium"
   - Builds mentor prompt with this context
   - Calls IBM Bob

3. Bob responds:
   "The `auth.py` file handles user authentication and session management.
    It imports `models.py` for the User schema and `utils.py` for token
    generation. This file is used by `main.py` and `router.py` to protect
    routes. Start by understanding the User model in `models.py` first."

4. Formatter structures response:
   {
     "answer": "The `auth.py` file handles...",
     "cited_files": [
       {"path": "services/auth.py", "reason": "Primary file"},
       {"path": "models.py", "reason": "Imported for User model"},
       {"path": "utils.py", "reason": "Token generation"}
     ],
     "related_files": ["main.py", "router.py"],
     "next_steps": ["Study models.py first", "Check utils.py tokens"],
     "confidence": 0.9
   }
```

---

## What is IN SCOPE

- Static analysis of Python repositories
- File-level dependency tracking (imports)
- Mentor-like Q&A about codebase structure
- Learning path recommendations
- Checkpoint quizzes for verification
- Integration with WatsonX Granite model
- Caching for performance

## What is OUT OF SCOPE

- Runtime analysis or profiling
- Binary/compiled file analysis
- Non-Python languages (Phase 1)
- Code execution or testing
- Git history analysis
- Security vulnerability scanning
- Real-time collaboration features
- IDE plugin development

---

## Key Design Decisions

### Why Bidirectional Dependencies?

**Problem:** "What breaks if I modify this file?"

**Solution:** Track both imports (what I depend on) AND imported_by (who depends on me). This enables impact analysis.

### Why Semantic Chunking?

**Problem:** Large files (>1000 LOC) exceed Bob's context window.

**Solution:** Split by classes/functions (semantic boundaries) rather than arbitrary line counts. Preserves code meaning.

### Why Query Classification?

**Problem:** Generic prompts produce generic answers.

**Solution:** Classify questions into types (file_purpose, where_to_start, impact_analysis) and use specialized prompt templates.

### Why Cache Repository Structure?

**Problem:** Parsing large repos on every query is slow.

**Solution:** Parse once, cache the file tree + dependency graph, invalidate on repo changes.

---

## Integration Points

### With Karl's Service

**Expected Data Format:**
```json
{
  "file_path": "services/auth.py",
  "complexity": 0.65,
  "centrality": 0.82,
  "distance_from_entry": 2,
  "recommendation": "study_later"
}
```

**Usage:** Inject these scores into Bob's context to influence learning path recommendations.

### With Ali Jan's UI

**API Endpoints:**
- `POST /api/v1/generate-roadmap` - Initial onboarding roadmap
- `POST /api/v1/ask` - Interactive Q&A
- `GET /health` - Service health check

**Response Format:** Always JSON with consistent error structure.

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Repository parsing | < 2s | First-time setup, cached after |
| Context retrieval | < 100ms | Per-query, must be fast |
| Bob API call | < 5s | Network + model inference |
| Total /ask response | < 6s | Acceptable for interactive use |
| Cache hit rate | > 90% | Most queries reuse context |

---

## Error Handling Strategy

1. **Invalid Repository Path** → Return 422 with clear message
2. **WatsonX API Timeout** → Return fallback response + log error
3. **Parsing Failure** → Use mock data + warn user
4. **Large File (>10k LOC)** → Chunk aggressively + warn about limits
5. **No Relevant Context** → Return general guidance + suggest rephrase

---

## Testing Philosophy

Following SKILL.md protocols:

1. **TDD (Test-Driven Development)**
   - Write test for behavior first (RED)
   - Implement minimal code to pass (GREEN)
   - Refactor without breaking tests

2. **Behavior-Focused Tests**
   - Test public interfaces, not implementation
   - Tests should survive refactoring
   - Example: "User can ask about file purpose" not "prompt_builder returns string"

3. **Vertical Slicing**
   - One behavior at a time, end-to-end
   - Not all tests first, then all implementation

---

## Vocabulary Usage Examples

**Good:** "The context retrieval service builds a bidirectional dependency graph to enable impact analysis queries."

**Bad:** "The thing that gets files also tracks what imports what."

**Good:** "We use semantic chunking to split large files at class boundaries, preserving code meaning within Bob's context window."

**Bad:** "We split big files into smaller pieces so the AI can read them."

---

## Next Steps

1. Review this context document with team
2. Ensure all stakeholders use consistent terminology
3. Update as new patterns emerge
4. Reference in all technical discussions

---

**Last Updated:** 2026-05-16  
**Owner:** Harshal (IBM Bob Orchestration)  
**Reviewers:** Team Lead, Karl, Ali Jan