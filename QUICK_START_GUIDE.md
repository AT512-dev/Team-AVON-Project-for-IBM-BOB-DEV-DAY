# 🚀 Quick Start Guide - Harshal's Implementation

## 📋 TL;DR

You're building the **IBM Bob Mentor System** - transforming WatsonX into an intelligent technical mentor that understands repository structure and guides new developers through codebases.

**Current Status:** Planning complete ✅  
**Next Step:** Switch to Code mode and start implementation

---

## 🎯 Your Core Responsibilities

1. **Enhanced Mentor Prompts** - Make Bob answer like a senior dev, not a chatbot
2. **Interactive /ask Endpoint** - Q&A loop with file-aware context
3. **Context Retrieval** - Smart file selection based on queries
4. **Dependency Integration** - Use Karl's scores to recommend learning paths

---

## 📂 Key Files You'll Work With

### Existing Files (to modify)
- [`bob_core/bob_service.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/bob_service.py:1) - WatsonX API calls
- [`bob_core/main.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/main.py:1) - FastAPI endpoints
- [`engine/parser.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/engine/parser.py:1) - Repository parsing
- [`engine/metrics.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/engine/metrics.py:1) - Complexity scoring

### New Files (to create)
- `bob_core/prompts.py` - Mentor prompt templates
- `bob_core/context_service.py` - Context retrieval logic
- `bob_core/response_formatter.py` - Structure Bob's responses
- `bob_core/chunking.py` - Split large files semantically
- `bob_core/dependency_integration.py` - Karl's score integration
- `tests/test_*.py` - Test suite

---

## 🔄 Implementation Phases

### Phase 1: Foundation (Days 1-2) ⭐ START HERE
```
✅ CONTEXT.md created
✅ IMPLEMENTATION_PLAN.md created
⏳ Set up branch: git checkout -b feature/harshal-watsonx-mentor
⏳ Verify WatsonX credentials
⏳ Build prompt template system
```

### Phase 2: Core Mentor Loop (Days 3-4)
```
⏳ Create context retrieval service
⏳ Build /ask endpoint
⏳ Implement query classification
⏳ Format responses for UI
```

### Phase 3: Advanced Features (Days 5-6)
```
⏳ Integrate Karl's dependency scores
⏳ Implement semantic chunking
⏳ Add relationship mapping
```

### Phase 4: Testing & Docs (Day 7)
```
⏳ Write comprehensive tests
⏳ Document API contracts
⏳ Create example queries
```

---

## 🎨 Ready-to-Use Prompts for Code Mode

### When Starting Implementation

```
Here is my project context, use this vocabulary throughout our session:
[PASTE CONTEXT.md]

I'm implementing the IBM Bob Mentor System for Compass AI. I need to start with Phase 1: Enhanced Mentor Prompts.

Current state:
- Basic WatsonX integration exists in bob_service.py
- Generic prompts need to become mentor-like
- Need to create bob_core/prompts.py with template system

Let's use GRILL MODE first to clarify the prompt architecture before writing code.
```

### When Writing Code (TDD Mode)

```
You are doing Test-Driven Development with strict red-green-refactor.

My project: Compass AI - IBM Bob Mentor System
My task: Implement prompt template system in bob_core/prompts.py

Core behaviors to test:
1. Build mentor prompt with repository context
2. Select appropriate template based on query type
3. Inject file relationships into context
4. Handle missing context gracefully

Start by confirming the public interface for the prompt builder.
```

### When Debugging

```
You are a disciplined debugging collaborator.

My project: Compass AI - IBM Bob Mentor System
The bug: [DESCRIBE EXACT ISSUE]

Start with step 1: let's confirm the exact reproduction.
```

---

## 📊 Architecture Quick Reference

```
User Question
    ↓
/ask Endpoint (main.py)
    ↓
Context Retriever (context_service.py)
    ├→ Get file content
    ├→ Get dependencies
    └→ Get complexity scores
    ↓
Prompt Builder (prompts.py)
    ├→ Select template
    ├→ Inject context
    └→ Format for WatsonX
    ↓
IBM Bob (bob_service.py)
    ↓
Response Formatter (response_formatter.py)
    ├→ Parse raw text
    ├→ Extract cited files
    └→ Structure as JSON
    ↓
Return to UI
```

---

## 🔑 Key Design Patterns

### 1. Prompt Template System
```python
# Three-layer approach
BASE_MENTOR_PROMPT (constant persona)
    + REPOSITORY_CONTEXT (cached per repo)
    + QUERY_SPECIFIC_CONTEXT (per question)
    = FINAL_PROMPT
```

### 2. Context Retrieval Strategy
```python
# Smart file selection
if focus_file:
    return file + immediate_dependencies
else:
    return top_N_important_files
```

### 3. Query Classification
```python
# Route to appropriate template
"What does X do?" → file_purpose template
"Where to start?" → where_to_start template
"What breaks if?" → impact_analysis template
else → general template
```

---

## 🧪 Testing Strategy

### Unit Tests
- Prompt builder with various inputs
- Context retrieval accuracy
- Query classification logic
- Response formatting

### Integration Tests
- End-to-end /ask flow
- WatsonX API integration
- Error handling

### Quality Tests
- Manual review of 50 sample responses
- Response time benchmarks
- Edge case handling

---

## 📝 API Contract for Ali Jan

### POST /api/v1/ask

**Request:**
```json
{
  "repo_path": "/path/to/repo",
  "question": "What does auth.py do?",
  "current_file": "services/auth.py",
  "context": {
    "task": "understanding authentication"
  }
}
```

**Response:**
```json
{
  "answer": "The `auth.py` file handles...",
  "cited_files": [
    {
      "path": "services/auth.py",
      "reason": "Primary file in question",
      "complexity": "Medium"
    }
  ],
  "related_files": ["models.py", "utils.py"],
  "next_steps": [
    "Study models.py for User schema",
    "Check utils.py for token helpers"
  ],
  "confidence": 0.85
}
```

---

## 🔗 Integration with Karl

**Expected from Karl:**
```json
{
  "file_path": "services/auth.py",
  "complexity": 0.65,
  "centrality": 0.82,
  "distance_from_entry": 2,
  "recommendation": "study_later"
}
```

**How you'll use it:**
- Inject scores into Bob's context
- Influence "where to start" recommendations
- Sort learning paths by complexity + centrality

---

## ⚡ Performance Targets

| Operation | Target | Why |
|-----------|--------|-----|
| Context retrieval | < 100ms | Per-query, must be fast |
| Bob API call | < 5s | Network + inference |
| Total /ask response | < 6s | Interactive use |
| Cache hit rate | > 90% | Reuse parsed repos |

---

## 🚨 Common Pitfalls to Avoid

1. **Don't dump entire files into Bob's context** → Use chunking
2. **Don't use generic prompts** → Classify queries and use templates
3. **Don't ignore dependencies** → Build bidirectional graph
4. **Don't skip error handling** → WatsonX API can timeout
5. **Don't write all tests first** → TDD = one test, one implementation, repeat

---

## 📚 Reference Documents

- [`CONTEXT.md`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/CONTEXT.md:1) - Domain vocabulary
- [`IMPLEMENTATION_PLAN.md`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/IMPLEMENTATION_PLAN.md:1) - Detailed plan
- [`bob_core/bob_service.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/bob_service.py:1) - Current WatsonX integration
- [`bob_core/main.py`](Team-AVON-Project-for-IBM-BOB-DEV-DAY/bob_core/main.py:19) - Existing endpoints

---

## 🎯 Success Criteria

You're done when:
- [ ] Bob responds like a senior dev, not a chatbot
- [ ] /ask endpoint returns structured, file-aware answers
- [ ] Responses cite specific files with relationships
- [ ] Integration with Karl's scores works
- [ ] Tests pass with >80% coverage
- [ ] API contracts documented for Ali Jan
- [ ] Response time < 6 seconds

---

## 🚀 Next Actions

1. **Review this guide** - Make sure you understand the architecture
2. **Check CONTEXT.md** - Familiarize with domain terms
3. **Switch to Code mode** - Use the prompts above
4. **Start with Phase 1** - Prompt template system first
5. **Follow TDD** - One test, one implementation, repeat

---

## 💡 Pro Tips

- **Use GRILL MODE** before writing code to clarify design
- **Reference CONTEXT.md** in every Code mode session
- **Test behaviors, not implementation** - tests should survive refactors
- **Commit frequently** - small, atomic commits
- **Ask for help** - coordinate with Karl and Ali Jan early

---

**Ready to code?** Switch to Code mode and paste the "When Starting Implementation" prompt above! 🚀