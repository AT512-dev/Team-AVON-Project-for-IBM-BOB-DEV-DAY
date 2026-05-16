# 🎯 Compass AI - Harshal's Implementation Plan
## IBM Bob WatsonX Mentor Integration

---

## 📋 Executive Summary

**Goal:** Transform IBM Bob from a generic code assistant into an intelligent technical mentor that understands repository structure, dependency relationships, and can guide new developers through complex codebases.

**Timeline:** Phased approach with incremental delivery
**Primary Stakeholder:** Ali Jan (UI), Karl (Dependency Graph)

---

## 🏗️ Architecture Overview

```mermaid
graph TB
    UI[Ali Jan's UI] -->|Question + Context| ASK[/ask Endpoint]
    ASK -->|Route Query| CTX[Context Retrieval Service]
    CTX -->|Fetch Files| REPO[Repository Parser]
    CTX -->|Get Scores| DEP[Dependency Graph]
    CTX -->|Build Context| PROMPT[Prompt Builder]
    PROMPT -->|Enhanced Prompt| BOB[IBM Bob WatsonX]
    BOB -->|Raw Response| FMT[Response Formatter]
    FMT -->|Structured JSON| UI
    
    REPO -->|File Tree| CACHE[Context Cache]
    DEP -->|Complexity Scores| CACHE
    CACHE -->|Fast Lookup| CTX
```

---

## 📚 Domain Vocabulary (CONTEXT.md)

| Term | Definition |
|------|------------|
| **Mentor Prompt** | System instruction that makes Bob respond like a senior engineer, not a generic chatbot |
| **Context Window** | The file content + dependency info fed to Bob per query |
| **Dependency Radius** | Karl's metric: complexity score + architectural distance from entry points |
| **Chunking Strategy** | How we split large files into digestible pieces for Bob's context |
| **Grounding Context** | Repository structure + file relationships that Bob reasons over |
| **Interactive Loop** | Question → Context Retrieval → Bob Response → UI Display cycle |
| **File-Aware Response** | Bob's answer that cites specific files and explains relationships |
| **Relationship Mapping** | Which files import/depend on which (bidirectional graph) |

---

## 🎯 Phase 1: Foundation (Days 1-2)

### 1.1 Project Setup
**Priority:** CRITICAL
**Dependencies:** None

**Tasks:**
- [ ] Create `CONTEXT.md` with vocabulary above
- [ ] Set up branch: `git checkout -b feature/harshal-watsonx-mentor`
- [ ] Verify WatsonX credentials in `.env`
- [ ] Test basic API connectivity with simple prompt
- [ ] Document current API response format

**Acceptance Criteria:**
- Can successfully call WatsonX API
- Response time < 5 seconds for simple queries
- Error handling works for invalid credentials

**Files to Create:**
- `CONTEXT.md`
- `tests/test_watsonx_connection.py`

---

### 1.2 Enhanced Mentor Prompt System
**Priority:** CRITICAL
**Dependencies:** 1.1

**Current Problem:**
```python
# bob_service.py line 34 - Too generic
prompt = f"You are a senior engineer onboarding a new developer..."
```

**Solution Design:**
Create a **Prompt Template System** with three layers:

1. **Base Mentor Persona** (constant)
2. **Repository Context** (per-repo, cached)
3. **Query-Specific Context** (per-question)

**Implementation:**

```python
# bob_core/prompts.py (NEW FILE)

BASE_MENTOR_PROMPT = """You are a senior technical mentor for the {repo_name} codebase.

Your role:
- Guide new developers through the codebase architecture
- Explain file purposes and relationships in plain English
- Recommend learning paths based on complexity and dependencies
- Cite specific files when explaining concepts
- Warn about architectural impacts of changes

Your knowledge:
- Complete file tree and import graph
- Dependency complexity scores (Easy/Medium/Hard)
- Which files are central vs peripheral
- Common entry points and data flow

Response style:
- Concise and practical (2-3 paragraphs max)
- Always cite specific files using format: `filename.ext`
- Use analogies when explaining complex patterns
- Prioritize actionable guidance over theory
"""

QUERY_TEMPLATES = {
    "file_purpose": """
Repository Context:
{repo_structure}

File in Question: {file_path}
Imports: {imports}
Imported By: {imported_by}
Complexity: {complexity}

Question: {user_question}

Explain this file's purpose, its role in the system, and which files depend on it.
""",
    
    "where_to_start": """
Repository Context:
{repo_structure}

Task: {task_description}

Available Files (sorted by learning order):
{ranked_files}

Question: {user_question}

Recommend which files to study first and why, considering complexity and centrality.
""",
    
    "impact_analysis": """
Repository Context:
{repo_structure}

File to Modify: {file_path}
Direct Dependencies: {direct_deps}
Reverse Dependencies: {reverse_deps}

Question: {user_question}

Explain what would break if this file is modified, and which tests should be updated.
""",
    
    "general": """
Repository Context:
{repo_structure}

Current Focus: {current_file}

Question: {user_question}

Answer based on the repository structure and file relationships.
"""
}

def build_mentor_prompt(
    query_type: str,
    repo_context: dict,
    user_question: str,
    **kwargs
) -> str:
    """Build context-aware prompt for IBM Bob"""
    base = BASE_MENTOR_PROMPT.format(repo_name=repo_context.get("name", "this project"))
    template = QUERY_TEMPLATES.get(query_type, QUERY_TEMPLATES["general"])
    
    context_vars = {
        "repo_structure": format_repo_structure(repo_context),
        "user_question": user_question,
        **kwargs
    }
    
    query_prompt = template.format(**context_vars)
    return f"{base}\n\n{query_prompt}"
```

**Acceptance Criteria:**
- Prompts include file relationships
- Responses cite specific files
- Complexity scores influence recommendations
- Different query types get appropriate context

**Files to Create:**
- `bob_core/prompts.py`
- `tests/test_prompt_builder.py`

---

## 🎯 Phase 2: Core Mentor Loop (Days 3-4)

### 2.1 Context Retrieval Service
**Priority:** CRITICAL
**Dependencies:** 1.2

**Purpose:** Intelligently fetch relevant files and relationships for each query

**Implementation:**

```python
# bob_core/context_service.py (NEW FILE)

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class FileContext:
    path: str
    content: str
    imports: List[str]
    imported_by: List[str]
    complexity: str
    loc: int

@dataclass
class RepoContext:
    name: str
    entry_points: List[str]
    file_tree: Dict[str, FileContext]
    dependency_graph: Dict[str, List[str]]
    
class ContextRetriever:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo_map = None
        self.reverse_deps = {}
        self._build_context()
    
    def _build_context(self):
        """Build complete repository context with bidirectional dependencies"""
        from engine.parser import parse_repository
        from engine.metrics import compute_complexity, rank_files_by_importance
        
        self.repo_map = parse_repository(self.repo_path)
        
        # Build reverse dependency map
        for file_path, imports in self.repo_map.files.items():
            for imported_file in imports:
                if imported_file not in self.reverse_deps:
                    self.reverse_deps[imported_file] = []
                self.reverse_deps[imported_file].append(file_path)
    
    def get_file_context(self, file_path: str) -> Optional[FileContext]:
        """Get complete context for a specific file"""
        if file_path not in self.repo_map.files:
            return None
        
        imports = self.repo_map.files[file_path]
        imported_by = self.reverse_deps.get(file_path, [])
        complexity = compute_complexity(file_path, imports)
        
        return FileContext(
            path=file_path,
            content=self._read_file(file_path),
            imports=imports,
            imported_by=imported_by,
            complexity=complexity,
            loc=self._count_loc(file_path)
        )
    
    def get_relevant_context(
        self, 
        query: str, 
        focus_file: Optional[str] = None,
        max_files: int = 5
    ) -> Dict:
        """Get relevant files based on query and optional focus file"""
        if focus_file:
            # Get file + its immediate dependencies
            context = self.get_file_context(focus_file)
            related_files = context.imports + context.imported_by
            return {
                "focus": context,
                "related": [self.get_file_context(f) for f in related_files[:max_files]]
            }
        
        # For general queries, return high-importance files
        from engine.metrics import rank_files_by_importance
        ranked = rank_files_by_importance(self.repo_map.files)
        top_files = [f[0] for f in ranked[:max_files]]
        
        return {
            "focus": None,
            "related": [self.get_file_context(f) for f in top_files]
        }
    
    def _read_file(self, file_path: str) -> str:
        """Read file content with error handling"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def _count_loc(self, file_path: str) -> int:
        """Count lines of code"""
        from engine.metrics import count_lines_of_code
        return count_lines_of_code(file_path)
```

**Acceptance Criteria:**
- Can retrieve file context in < 100ms
- Bidirectional dependencies work correctly
- Handles missing files gracefully
- Caches repo structure for performance

**Files to Create:**
- `bob_core/context_service.py`
- `tests/test_context_retrieval.py`

---

### 2.2 /ask Endpoint Implementation
**Priority:** CRITICAL
**Dependencies:** 2.1, 1.2

**API Contract:**

```python
# Request
POST /api/v1/ask
{
    "repo_path": "/path/to/repo",
    "question": "What does auth.service.js do?",
    "current_file": "services/auth.py",  // optional
    "context": {  // optional
        "task": "understanding authentication flow"
    }
}

# Response
{
    "answer": "The `auth.py` file handles user authentication...",
    "cited_files": [
        {
            "path": "services/auth.py",
            "reason": "Primary file in question",
            "complexity": "Medium"
        },
        {
            "path": "models.py",
            "reason": "Imported for User model",
            "complexity": "Easy"
        }
    ],
    "related_files": ["utils.py", "database.py"],
    "next_steps": [
        "Study models.py to understand User schema",
        "Check utils.py for helper functions"
    ],
    "confidence": 0.85
}
```

**Implementation:**

```python
# bob_core/main.py - ADD THIS ENDPOINT

from bob_core.context_service import ContextRetriever
from bob_core.prompts import build_mentor_prompt
from bob_core.response_formatter import format_mentor_response

class AskRequest(BaseModel):
    repo_path: str
    question: str
    current_file: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.post("/api/v1/ask")
async def ask_mentor(request: AskRequest):
    """Interactive Q&A with IBM Bob mentor"""
    
    # 1. Retrieve relevant context
    retriever = ContextRetriever(request.repo_path)
    context = retriever.get_relevant_context(
        query=request.question,
        focus_file=request.current_file
    )
    
    # 2. Determine query type
    query_type = classify_query(request.question)
    
    # 3. Build enhanced prompt
    prompt = build_mentor_prompt(
        query_type=query_type,
        repo_context={
            "name": os.path.basename(request.repo_path),
            "files": retriever.repo_map.files
        },
        user_question=request.question,
        file_path=request.current_file,
        imports=context["focus"].imports if context["focus"] else [],
        imported_by=context["focus"].imported_by if context["focus"] else [],
        complexity=context["focus"].complexity if context["focus"] else "Unknown"
    )
    
    # 4. Call IBM Bob
    raw_response = await generate_mentor_response(prompt)
    
    # 5. Format for UI
    formatted = format_mentor_response(
        raw_response=raw_response,
        context=context,
        query_type=query_type
    )
    
    return formatted

def classify_query(question: str) -> str:
    """Classify question type for appropriate prompt template"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["what does", "purpose", "role"]):
        return "file_purpose"
    elif any(word in question_lower for word in ["where to start", "begin", "first"]):
        return "where_to_start"
    elif any(word in question_lower for word in ["break", "impact", "modify", "change"]):
        return "impact_analysis"
    else:
        return "general"
```

**Acceptance Criteria:**
- Endpoint responds in < 5 seconds
- Returns structured JSON with cited files
- Handles invalid repo paths gracefully
- Query classification works for common patterns

**Files to Modify:**
- `bob_core/main.py` (add endpoint)

**Files to Create:**
- `bob_core/response_formatter.py`
- `tests/test_ask_endpoint.py`

---

## 🎯 Phase 3: Advanced Features (Days 5-6)

### 3.1 Karl's Dependency Graph Integration
**Priority:** HIGH
**Dependencies:** 2.2

**Coordination Point:** Need Karl's API contract or data format

**Expected Integration:**

```python
# bob_core/dependency_integration.py (NEW FILE)

class DependencyScoreProvider:
    """Interface to Karl's dependency graph service"""
    
    def get_file_score(self, file_path: str) -> Dict:
        """
        Get Karl's dependency radius score
        
        Returns:
        {
            "complexity": float,  # 0-1 scale
            "centrality": float,  # 0-1 scale (how many files depend on it)
            "distance_from_entry": int,  # hops from main.py
            "recommendation": "start_here" | "study_later" | "advanced"
        }
        """
        # TODO: Call Karl's service or read from shared cache
        pass
    
    def get_learning_path(self, task: str) -> List[str]:
        """Get recommended file order based on dependency scores"""
        pass
```

**Integration into Context:**
- Add dependency scores to `FileContext`
- Use scores in "where_to_start" query type
- Influence file ranking in context retrieval

**Acceptance Criteria:**
- Can fetch Karl's scores (mock if not ready)
- Scores influence Bob's recommendations
- Learning path respects complexity + centrality

**Files to Create:**
- `bob_core/dependency_integration.py`
- `tests/test_dependency_integration.py`

---

### 3.2 Intelligent Chunking Strategy
**Priority:** MEDIUM
**Dependencies:** 2.1

**Problem:** Large files (>1000 LOC) exceed Bob's context window

**Solution:** Semantic chunking based on code structure

```python
# bob_core/chunking.py (NEW FILE)

import ast
from typing import List, Dict

class CodeChunker:
    """Split large files into semantic chunks"""
    
    MAX_CHUNK_SIZE = 500  # lines
    
    def chunk_python_file(self, content: str) -> List[Dict]:
        """
        Split Python file by top-level definitions
        
        Returns chunks like:
        [
            {
                "type": "imports",
                "lines": "1-15",
                "content": "import statements..."
            },
            {
                "type": "class",
                "name": "UserService",
                "lines": "16-150",
                "content": "class definition..."
            }
        ]
        """
        try:
            tree = ast.parse(content)
            chunks = []
            
            # Extract imports
            imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
            if imports:
                chunks.append({
                    "type": "imports",
                    "lines": f"1-{imports[-1].lineno}",
                    "content": self._extract_lines(content, 1, imports[-1].lineno)
                })
            
            # Extract classes and functions
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    chunks.append({
                        "type": "class" if isinstance(node, ast.ClassDef) else "function",
                        "name": node.name,
                        "lines": f"{node.lineno}-{node.end_lineno}",
                        "content": self._extract_lines(content, node.lineno, node.end_lineno)
                    })
            
            return chunks
        except:
            # Fallback: split by line count
            return self._chunk_by_lines(content)
    
    def get_relevant_chunks(self, chunks: List[Dict], query: str) -> List[Dict]:
        """Select most relevant chunks based on query"""
        # Simple keyword matching for now
        # TODO: Use embeddings for semantic similarity
        keywords = query.lower().split()
        scored_chunks = []
        
        for chunk in chunks:
            score = sum(1 for kw in keywords if kw in chunk["content"].lower())
            scored_chunks.append((score, chunk))
        
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored_chunks[:3]]
```

**Acceptance Criteria:**
- Can chunk files >500 LOC
- Preserves semantic boundaries (classes, functions)
- Retrieves relevant chunks based on query
- Fallback for non-Python files

**Files to Create:**
- `bob_core/chunking.py`
- `tests/test_chunking.py`

---

## 🎯 Phase 4: Testing & Documentation (Day 7)

### 4.1 Test Suite
**Priority:** HIGH
**Dependencies:** All previous phases

**Test Categories:**

1. **Unit Tests**
   - Prompt builder with various query types
   - Context retrieval accuracy
   - Chunking logic
   - Response formatting

2. **Integration Tests**
   - End-to-end /ask flow
   - WatsonX API integration
   - Dependency score integration

3. **Quality Tests**
   - Mentor response quality (manual review)
   - Response time benchmarks
   - Error handling coverage

**Files to Create:**
- `tests/test_mentor_quality.py`
- `tests/test_integration.py`
- `tests/test_performance.py`

---

### 4.2 Documentation
**Priority:** HIGH
**Dependencies:** 4.1

**Documents to Create:**

1. **API_CONTRACTS.md** - For Ali Jan
   - `/ask` endpoint specification
   - Request/response examples
   - Error codes and handling
   - Rate limits and timeouts

2. **INTEGRATION_GUIDE.md** - For Karl
   - How to provide dependency scores
   - Data format expectations
   - Caching strategy
   - Update frequency

3. **EXAMPLE_QUERIES.md**
   - 20+ example questions with expected responses
   - Edge cases and error scenarios
   - Performance benchmarks

**Files to Create:**
- `docs/API_CONTRACTS.md`
- `docs/INTEGRATION_GUIDE.md`
- `docs/EXAMPLE_QUERIES.md`

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time | < 5s | 95th percentile |
| Answer Relevance | > 80% | Manual review of 50 queries |
| File Citation Accuracy | > 90% | Automated validation |
| Dependency Integration | 100% | Karl's scores used in all responses |
| Test Coverage | > 85% | pytest-cov |
| API Uptime | > 99% | Health check monitoring |

---

## 🚀 Deployment Checklist

- [ ] Environment variables documented in `.env.example`
- [ ] WatsonX credentials secured (not in git)
- [ ] API rate limits configured
- [ ] Error logging to file + console
- [ ] Health check endpoint working
- [ ] CORS configured for Ali Jan's UI
- [ ] Docker container builds successfully
- [ ] README updated with setup instructions

---

## 🔄 Iteration Strategy

After Phase 4, gather feedback and iterate on:

1. **Prompt Quality** - Refine based on actual developer questions
2. **Context Relevance** - Improve file selection algorithm
3. **Response Format** - Adjust based on UI needs
4. **Performance** - Optimize slow queries
5. **Edge Cases** - Handle unusual repo structures

---

## 📞 Coordination Points

| Stakeholder | What They Need | When |
|-------------|----------------|------|
| **Ali Jan (UI)** | `/ask` API contract | End of Phase 2 |
| **Karl (Dependency)** | Score format specification | Start of Phase 3 |
| **Team Lead** | Progress updates | Daily standup |
| **QA** | Test scenarios | End of Phase 3 |

---

## 🎓 Learning Resources

- WatsonX API Documentation
- RAG (Retrieval-Augmented Generation) patterns
- AST parsing in Python
- FastAPI async patterns
- Prompt engineering best practices

---

## ⚠️ Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| WatsonX API downtime | HIGH | Implement fallback responses |
| Large repo performance | MEDIUM | Aggressive caching + chunking |
| Karl's service not ready | MEDIUM | Mock dependency scores |
| Prompt quality issues | HIGH | Extensive testing + iteration |
| Context window limits | MEDIUM | Smart chunking + summarization |

---

## 🎯 Definition of Done

A task is complete when:
- [ ] Code written and tested (>80% coverage)
- [ ] Manual testing passed
- [ ] Documentation updated
- [ ] Code reviewed by team lead
- [ ] Integrated with dependent services
- [ ] Performance benchmarks met
- [ ] Error handling verified

---

**Next Step:** Review this plan, adjust priorities, then switch to Code mode to begin implementation.