# 📊 Compass AI - Implementation Plan Summary
## Harshal's IBM Bob Mentor System

---

## 🎯 Mission Statement

Transform IBM Bob (WatsonX) from a generic code assistant into an **intelligent technical mentor** that understands repository structure, dependency relationships, and can guide new developers through complex codebases like a senior engineer.

---

## 📈 Project Scope

### What We're Building

```
┌─────────────────────────────────────────────────────────────┐
│                    BEFORE (Current State)                    │
├─────────────────────────────────────────────────────────────┤
│ ❌ Generic prompts: "You are a senior engineer..."          │
│ ❌ No file relationship awareness                           │
│ ❌ No dependency context in responses                       │
│ ❌ Only /generate-roadmap endpoint exists                   │
│ ❌ No interactive Q&A capability                            │
└─────────────────────────────────────────────────────────────┘

                            ⬇️ TRANSFORMATION ⬇️

┌─────────────────────────────────────────────────────────────┐
│                     AFTER (Target State)                     │
├─────────────────────────────────────────────────────────────┤
│ ✅ Context-aware mentor prompts with repo structure         │
│ ✅ Bidirectional dependency graph (imports + imported_by)   │
│ ✅ File-aware responses citing specific files               │
│ ✅ Interactive /ask endpoint for Q&A                        │
│ ✅ Integration with Karl's complexity scores                │
│ ✅ Intelligent chunking for large files                     │
│ ✅ Structured responses for Ali Jan's UI                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview

```mermaid
graph LR
    A[Developer Question] --> B[/ask Endpoint]
    B --> C[Context Retriever]
    C --> D[Repository Parser]
    C --> E[Karl's Dependency Scores]
    C --> F[Prompt Builder]
    F --> G[IBM Bob WatsonX]
    G --> H[Response Formatter]
    H --> I[Structured JSON]
    I --> J[Ali Jan's UI]
    
    style B fill:#4CAF50
    style F fill:#2196F3
    style G fill:#FF9800
    style H fill:#9C27B0
```

---

## 📅 Implementation Timeline

### Phase 1: Foundation (Days 1-2) 🟢 CRITICAL PATH
- ✅ Create CONTEXT.md with domain vocabulary
- ⏳ Set up development branch
- ⏳ Verify WatsonX credentials
- ⏳ Design enhanced prompt architecture
- ⏳ Implement prompt template system

**Deliverable:** Mentor-like prompts that cite files and explain relationships

---

### Phase 2: Core Mentor Loop (Days 3-4) 🟢 CRITICAL PATH
- ⏳ Build context retrieval service
- ⏳ Create /ask endpoint
- ⏳ Implement query classification
- ⏳ Format responses for UI

**Deliverable:** Working /ask endpoint that Ali Jan can integrate

---

### Phase 3: Advanced Features (Days 5-6) 🟡 HIGH PRIORITY
- ⏳ Integrate Karl's dependency scores
- ⏳ Implement semantic chunking
- ⏳ Add relationship mapping

**Deliverable:** Optimized context retrieval with learning path recommendations

---

### Phase 4: Testing & Documentation (Day 7) 🟡 HIGH PRIORITY
- ⏳ Write comprehensive tests (>80% coverage)
- ⏳ Document API contracts
- ⏳ Create example queries

**Deliverable:** Production-ready system with documentation

---

## 🎨 Key Features

### 1. Enhanced Mentor Prompts

**Before:**
```python
prompt = "You are a senior engineer. Explain this code."
```

**After:**
```python
prompt = """
You are a technical mentor for the {repo_name} codebase.

File: services/auth.py
Imports: models.py, utils.py
Imported By: main.py, router.py
Complexity: Medium

Question: What does this file do?

Explain its purpose, relationships, and recommend learning order.
"""
```

---

### 2. Interactive /ask Endpoint

**Example Request:**
```json
POST /api/v1/ask
{
  "repo_path": "/path/to/repo",
  "question": "What does auth.py do?",
  "current_file": "services/auth.py"
}
```

**Example Response:**
```json
{
  "answer": "The `auth.py` file handles user authentication...",
  "cited_files": [
    {"path": "services/auth.py", "reason": "Primary file", "complexity": "Medium"},
    {"path": "models.py", "reason": "User model", "complexity": "Easy"}
  ],
  "related_files": ["utils.py", "database.py"],
  "next_steps": [
    "Study models.py to understand User schema",
    "Check utils.py for token generation"
  ],
  "confidence": 0.85
}
```

---

### 3. Context Retrieval Service

**Smart File Selection:**
- If user asks about specific file → return file + dependencies
- If general question → return top N important files
- Always include bidirectional relationships
- Cache repository structure for performance

**Bidirectional Dependencies:**
```python
auth.py:
  imports: [models.py, utils.py]
  imported_by: [main.py, router.py]
```

---

### 4. Query Classification

**Automatic Template Selection:**
- "What does X do?" → `file_purpose` template
- "Where should I start?" → `where_to_start` template
- "What breaks if I modify X?" → `impact_analysis` template
- Other questions → `general` template

---

### 5. Semantic Chunking

**Problem:** Large files (>1000 LOC) exceed Bob's context window

**Solution:** Split by semantic boundaries
```python
# Instead of arbitrary line splits
chunk_1 = lines[0:500]
chunk_2 = lines[500:1000]

# Use semantic boundaries
chunk_1 = imports_section
chunk_2 = UserService_class
chunk_3 = helper_functions
```

---

## 🔗 Integration Points

### With Ali Jan (UI Developer)

**What Ali Jan Needs:**
- `/ask` endpoint specification
- Request/response JSON format
- Error codes and handling
- Example queries

**Deliverable:** `docs/API_CONTRACTS.md`

---

### With Karl (Dependency Graph)

**What You Need from Karl:**
```json
{
  "file_path": "services/auth.py",
  "complexity": 0.65,
  "centrality": 0.82,
  "distance_from_entry": 2,
  "recommendation": "study_later"
}
```

**How You'll Use It:**
- Inject scores into Bob's context
- Influence learning path recommendations
- Sort files by complexity + centrality

**Deliverable:** `docs/INTEGRATION_GUIDE.md`

---

## 📊 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Response Time** | < 6s | 95th percentile of /ask requests |
| **Answer Relevance** | > 80% | Manual review of 50 sample queries |
| **File Citation Accuracy** | > 90% | Automated validation against repo |
| **Test Coverage** | > 85% | pytest-cov report |
| **API Uptime** | > 99% | Health check monitoring |

---

## 🧪 Testing Strategy

### Following SKILL.md TDD Protocol

**Red-Green-Refactor Loop:**
1. Write ONE failing test (behavior-focused)
2. Write MINIMAL code to pass it
3. Refactor without breaking tests
4. Repeat for next behavior

**Example Test:**
```python
def test_mentor_can_explain_file_purpose():
    """User can ask about file purpose and get cited response"""
    response = ask_mentor(
        question="What does auth.py do?",
        repo_path="/test/repo"
    )
    
    assert "auth.py" in response["answer"]
    assert len(response["cited_files"]) > 0
    assert response["cited_files"][0]["path"] == "services/auth.py"
```

---

## 🚨 Risk Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **WatsonX API downtime** | HIGH | Implement fallback responses + retry logic |
| **Large repo performance** | MEDIUM | Aggressive caching + chunking |
| **Karl's service not ready** | MEDIUM | Mock dependency scores for testing |
| **Prompt quality issues** | HIGH | Extensive testing + iteration |
| **Context window limits** | MEDIUM | Smart chunking + summarization |

---

## 📦 Deliverables Checklist

### Documentation
- [x] CONTEXT.md - Domain vocabulary
- [x] IMPLEMENTATION_PLAN.md - Detailed plan
- [x] QUICK_START_GUIDE.md - Quick reference
- [ ] API_CONTRACTS.md - For Ali Jan
- [ ] INTEGRATION_GUIDE.md - For Karl
- [ ] EXAMPLE_QUERIES.md - Sample Q&A

### Code
- [ ] bob_core/prompts.py - Prompt templates
- [ ] bob_core/context_service.py - Context retrieval
- [ ] bob_core/response_formatter.py - Response structuring
- [ ] bob_core/chunking.py - Semantic chunking
- [ ] bob_core/dependency_integration.py - Karl's integration
- [ ] /ask endpoint in main.py

### Tests
- [ ] test_prompt_builder.py
- [ ] test_context_retrieval.py
- [ ] test_ask_endpoint.py
- [ ] test_chunking.py
- [ ] test_integration.py

---

## 🎯 Definition of Done

A feature is complete when:
- ✅ Code written and tested (>80% coverage)
- ✅ Manual testing passed
- ✅ Documentation updated
- ✅ Code reviewed by team lead
- ✅ Integrated with dependent services
- ✅ Performance benchmarks met
- ✅ Error handling verified

---

## 🚀 Next Steps

### Immediate Actions (Today)
1. ✅ Review this plan with team
2. ⏳ Set up development branch
3. ⏳ Verify WatsonX credentials
4. ⏳ Start Phase 1: Prompt template system

### This Week
- Complete Phase 1 & 2 (Foundation + Core Loop)
- Coordinate with Ali Jan on API contract
- Coordinate with Karl on dependency scores

### Next Week
- Complete Phase 3 & 4 (Advanced Features + Testing)
- Integration testing with UI
- Documentation finalization

---

## 💬 Communication Plan

### Daily Standups
- Progress on current phase
- Blockers (if any)
- Coordination needs with Karl/Ali Jan

### Mid-Week Check-in
- Demo /ask endpoint to team
- Gather feedback on response quality
- Adjust priorities if needed

### End-of-Week Review
- Show working system
- Review test coverage
- Plan next iteration

---

## 📚 Resources

### Project Files
- [`CONTEXT.md`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/CONTEXT.md:1) - Domain vocabulary
- [`IMPLEMENTATION_PLAN.md`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/IMPLEMENTATION_PLAN.md:1) - Detailed technical plan
- [`QUICK_START_GUIDE.md`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/QUICK_START_GUIDE.md:1) - Quick reference for coding

### Existing Code
- [`bob_core/bob_service.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/bob_service.py:1) - WatsonX integration
- [`bob_core/main.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/main.py:1) - FastAPI endpoints
- [`engine/parser.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/engine/parser.py:1) - Repository parsing
- [`engine/metrics.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/engine/metrics.py:1) - Complexity metrics

---

## ✨ Vision

**End Goal:** A new developer joins the team, clones the repo, asks Compass AI "Where should I start to understand authentication?", and Bob responds:

> "Start with `models.py` (Easy complexity) to understand the User schema. This file is imported by `auth.py` and defines the core data structure. Once you're comfortable with the User model, move to `utils.py` to see how tokens are generated. Finally, study `auth.py` (Medium complexity) which ties everything together. This file is used by `main.py` and `router.py` to protect routes."

**That's the experience we're building.** 🚀

---

**Status:** Planning Complete ✅  
**Ready for:** Code Implementation  
**Owner:** Harshal  
**Last Updated:** 2026-05-16