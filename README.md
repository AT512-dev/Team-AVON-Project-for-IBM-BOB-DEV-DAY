# Compass AI - IBM Bob Mentor System

<div align="center">

> An intelligent AI-powered codebase navigation and mentoring system built for IBM's Bob Dev Day hackathon by Team AVON.

[![Tests](https://img.shields.io/badge/tests-167%20passed-brightgreen)](./TEST_RESULTS.md)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com/)
[![IBM WatsonX](https://img.shields.io/badge/IBM-WatsonX-blue)](https://www.ibm.com/watsonx)
[![Code Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](./TEST_RESULTS.md)


[Features](#-key-features) • [Quick Start](#-quick-start) • [Documentation](#-related-documentation) • [Contributing](CONTRIBUTING.md)

</div>

## 🎯 Overview

Compass AI is an intelligent mentor system that helps developers navigate unfamiliar codebases. Using IBM WatsonX AI and advanced dependency analysis, it provides context-aware guidance, learning paths, and architectural insights.

### Key Features

- 🤖 **AI-Powered Mentoring**: Context-aware responses using IBM WatsonX
- 🗺️ **Smart Navigation**: Dependency-based learning paths
- 📊 **Complexity Analysis**: Automatic file complexity scoring
- 🔍 **Semantic Search**: Find relevant code quickly
- 📚 **Interactive Q&A**: Ask questions about any file or concept
- 🎓 **Personalized Roadmaps**: Tailored learning paths based on your goals

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- IBM WatsonX API credentials
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Team-AVON-Project-for-IBM-BOB-DEV-DAY

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your IBM WatsonX credentials
```

### Environment Variables

Create a `.env` file with:

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Running the Server

```bash
# Start the FastAPI server
uvicorn bob_core.main:app --reload --port 8000

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=bob_core --cov-report=html
```

## 📖 Usage Examples

### 1. Ask About a File

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/repo",
    "question": "What does auth.py do?",
    "current_file": "services/auth.py"
  }'
```

**Response:**
```json
{
  "answer": "The auth.py file handles user authentication...",
  "cited_files": [
    {
      "path": "services/auth.py",
      "reason": "Primary file in question",
      "complexity": "Medium",
      "loc": 150
    }
  ],
  "related_files": ["models.py", "utils.py"],
  "next_steps": [
    "Study models.py to understand the User model",
    "Check utils.py for helper functions"
  ],
  "confidence": 0.85,
  "query_type": "file_purpose"
}
```

### 2. Get a Learning Roadmap

```bash
curl -X POST http://localhost:8000/api/v1/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/repo",
    "task_description": "Understand the authentication system"
  }'
```

### 3. Ask Where to Start

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/repo",
    "question": "Where should I start learning this codebase?"
  }'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Endpoints                         │
│  • /api/v1/ask - Interactive Q&A                            │
│  • /api/v1/generate-roadmap - Learning paths                │
│  • /health - Health check                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Context    │ │    Prompt    │ │   Response   │
│  Retrieval   │ │   Builder    │ │  Formatter   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    IBM WatsonX AI                            │
└─────────────────────────────────────────────────────────────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Dependency  │ │   Chunking   │ │   Metrics    │
│   Analysis   │ │    Engine    │ │  Calculator  │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 📚 Core Components

### 1. Context Retrieval (`bob_core/context_service.py`)
- Builds bidirectional dependency graphs
- Retrieves relevant file context
- Calculates impact radius
- Generates repository summaries

### 2. Prompt Builder (`bob_core/prompts.py`)
- Query classification (4 types)
- Context-aware prompt generation
- Repository structure formatting
- Mentor persona integration

### 3. Response Formatter (`bob_core/response_formatter.py`)
- Extracts cited files
- Identifies next steps
- Calculates confidence scores
- Structures responses for UI

### 4. Dependency Integration (`bob_core/dependency_integration.py`)
- Complexity scoring
- Learning path generation
- Entry point identification
- Centrality analysis

### 5. Chunking Engine (`bob_core/chunking.py`)
- Semantic code chunking
- Relevance scoring
- Large file handling
- Multi-language support

## 🧪 Testing

**Test Coverage: 100% (167/167 tests passing)**

- **Unit Tests**: 150+ tests covering all core modules
- **Integration Tests**: 15 end-to-end workflow tests
- **Edge Case Tests**: 32 boundary condition tests
- **Performance Tests**: Response time benchmarks

See [TEST_RESULTS.md](./TEST_RESULTS.md) for detailed test report.

## 📊 API Reference

### POST `/api/v1/ask`

Interactive Q&A with the AI mentor.

**Request Body:**
```typescript
{
  repo_path: string;        // Path to repository
  question: string;         // User's question
  current_file?: string;    // Optional: Current file context
  context?: object;         // Optional: Additional context
}
```

**Response:**
```typescript
{
  answer: string;           // AI-generated response
  cited_files: Array<{      // Files mentioned in response
    path: string;
    reason: string;
    complexity: string;
    loc: number;
  }>;
  related_files: string[];  // Related file paths
  next_steps: string[];     // Recommended actions
  confidence: number;       // 0-1 confidence score
  query_type: string;       // Query classification
}
```

### POST `/api/v1/generate-roadmap`

Generate a personalized learning roadmap.

**Request Body:**
```typescript
{
  repo_path: string;
  task_description?: string;
}
```

**Response:**
```typescript
{
  roadmap: Array<{
    file_path: string;
    complexity_score: string;
    learning_objective: string;
  }>;
  quiz: {
    questions: Array<object>;
  };
}
```

### GET `/health`

Health check endpoint.

**Response:**
```typescript
{
  status: "ok";
  service: "Compass AI";
}
```

## 🎓 Query Types

Compass AI automatically classifies queries into 4 types:

1. **File Purpose** - "What does auth.py do?"
2. **Where to Start** - "Where should I begin?"
3. **Impact Analysis** - "What breaks if I modify this?"
4. **General** - Other questions about the codebase

## 🔧 Configuration

### Complexity Thresholds

Adjust in `bob_core/dependency_integration.py`:

```python
COMPLEXITY_THRESHOLDS = {
    "easy": 0.3,    # 0-0.3: Easy
    "medium": 0.6,  # 0.3-0.6: Medium
    "hard": 1.0     # 0.6-1.0: Hard
}
```

### Context Limits

Adjust in `bob_core/context_service.py`:

```python
MAX_RELATED_FILES = 10
MAX_DEPENDENCY_DEPTH = 3
MAX_IMPACT_DEPTH = 2
```

## 🤝 Team AVON

- **Backend & AI Integration**: Core mentor system
- **Dependency Analysis**: Graph-based complexity scoring
- **UI Development**: Interactive navigation interface
- **Testing & QA**: Comprehensive test coverage

## 📄 License

This project was created for IBM's Bob Dev Day hackathon.

## 🔗 Related Documentation

- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
- [Test Results](./TEST_RESULTS.md)
- [API Contracts](./docs/API_CONTRACTS.md)
- [Example Queries](./docs/EXAMPLE_QUERIES.md)
- [Team Integration Guide](./TEAM_INTEGRATION_GUIDE.md)
- [Quick Start Guide](./QUICK_START_GUIDE.md)

## 🚀 Future Enhancements

- [ ] Real-time code analysis
- [ ] Multi-repository support
- [ ] Custom learning paths
- [ ] Code quality suggestions
- [ ] Integration with IDEs
- [ ] Collaborative features

---

**Made with ❤️ by Team AVON for IBM Bob Dev Day 2026**
