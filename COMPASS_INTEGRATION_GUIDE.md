# Compass AI Integration Guide

## Overview

This guide explains how the **engine layer** (parser, metrics, dependency_intelligence) connects to the **bob_core layer** (orchestration, context, prompts, Bob AI) to create the complete Compass AI onboarding experience.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Ali Jan)                       │
│                    POST /api/v1/compass/analyze                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    bob_core/main.py (FastAPI)                    │
│                  CompassAnalysisRequest Handler                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              bob_core/orchestration.py                           │
│                  CompassOrchestrator                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Step 1 & 2: Parse & Analyze Repository                 │    │
│  │ • Calls engine/dependency_intelligence.py              │    │
│  │ • Which uses engine/parser.py                          │    │
│  │ • And engine/metrics.py                                │    │
│  │ • Returns DependencyIntelligencePayload                │    │
│  └────────────────────────────────────────────────────────┘    │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Step 3: Chunk Critical Files                           │    │
│  │ • Uses bob_core/chunking.py                            │    │
│  │ • Breaks large files into semantic chunks              │    │
│  │ • Avoids token limit issues                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Step 4: Generate AI Explanations                       │    │
│  │ • Uses bob_core/bob_service.py                         │    │
│  │ • Calls IBM WatsonX API                                │    │
│  │ • Generates plain-English explanations                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Step 5: Format Response                                │    │
│  │ • Uses bob_core/response_formatter.py                  │    │
│  │ • Creates constellation graph                          │    │
│  │ • Builds learning roadmap                              │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         JSON Response                            │
│  {                                                               │
│    "status": "success",                                          │
│    "dependency_radius_score": 8.5,                               │
│    "learning_roadmap": [...],                                    │
│    "constellation_graph": {...}                                  │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Engine Layer (Karl's Work)

#### `engine/parser.py`
- **Purpose**: Scans repository and extracts file structure
- **Key Functions**:
  - `analyze_repository_files()`: Parses all source files
  - `parse_python_file()`: Extracts imports, exports, symbols from Python
  - `parse_js_like_file()`: Handles JavaScript/TypeScript files
- **Output**: Dictionary of `FileAnalysis` objects with imports/exports

#### `engine/metrics.py`
- **Purpose**: Calculates complexity and importance metrics
- **Key Functions**:
  - `compute_numeric_complexity()`: 0-100 complexity score
  - `compute_importance_score()`: 0-100 importance score
  - `infer_architectural_layer()`: Categorizes files by layer
  - `build_reverse_graph()`: Creates "who imports me" map
- **Output**: Numeric scores and architectural classifications

#### `engine/dependency_intelligence.py`
- **Purpose**: Orchestrates complete dependency analysis
- **Key Function**: `build_dependency_intelligence(repo_path)`
- **Output**: `DependencyIntelligencePayload` containing:
  - `nodes`: List of `DependencyNode` objects (one per file)
  - `edges`: List of `DependencyEdge` objects (imports)
  - `roadmap`: Pre-calculated learning order
  - `summary`: High-level statistics
  - `clusters`: Files grouped by architectural layer

### 2. Bob Core Layer

#### `bob_core/orchestration.py` ⭐ NEW
- **Purpose**: Main workflow coordinator
- **Class**: `CompassOrchestrator`
- **Key Methods**:
  - `analyze_repository()`: Calls engine layer
  - `generate_learning_roadmap()`: Creates roadmap with AI explanations
  - `generate_constellation_graph()`: Formats graph for frontend
  - `generate_complete_analysis()`: **Main entry point**

#### `bob_core/dependency_integration.py` ⭐ UPDATED
- **Purpose**: Bridge between engine layer and bob_core
- **Class**: `DependencyScoreProvider`
- **Changes**:
  - Now uses real `build_dependency_intelligence()` instead of mocks
  - Converts `DependencyNode` to `DependencyScore`
  - Provides unified interface for accessing dependency data

#### `bob_core/chunking.py`
- **Purpose**: Splits large files into semantic chunks
- **Class**: `CodeChunker`
- **Why**: Prevents token limit issues when sending code to AI

#### `bob_core/bob_service.py`
- **Purpose**: Communicates with IBM WatsonX AI
- **Key Function**: `generate_explanation(file_context, task)`
- **Output**: Plain-English explanation of file's purpose

#### `bob_core/response_formatter.py` ⭐ UPDATED
- **Purpose**: Formats data for frontend consumption
- **New Function**: `format_compass_response()`
- **Output**: Exact JSON structure Ali Jan needs

#### `bob_core/main.py` ⭐ UPDATED
- **Purpose**: FastAPI application entry point
- **New Endpoint**: `POST /api/v1/compass/analyze`
- **Request Body**:
  ```json
  {
    "repo_path": "/path/to/repo",
    "task_description": "Understand the codebase",
    "max_roadmap_files": 10,
    "include_tests": false
  }
  ```

## Usage Example

### 1. Start the Backend

```bash
cd bob_core
uvicorn main:app --reload --port 8000
```

### 2. Call the API

```bash
curl -X POST http://localhost:8000/api/v1/compass/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/your/repo",
    "task_description": "Understand the authentication system",
    "max_roadmap_files": 10
  }'
```

### 3. Response Structure

```json
{
  "status": "success",
  "dependency_radius_score": 8.5,
  "learning_roadmap": [
    {
      "step": 1,
      "file_path": "src/config/database.js",
      "dependencies_count": 14,
      "priority": "critical",
      "bob_explanation": "This file establishes the database connection pool and exports configuration for all data access layers. Start here because it's a foundational dependency with no prerequisites.",
      "architectural_layer": "Database Layer",
      "complexity_score": 45,
      "dependency_radius": 0
    },
    {
      "step": 2,
      "file_path": "src/models/user.js",
      "dependencies_count": 3,
      "priority": "high",
      "bob_explanation": "Defines the User data model and validation schemas. Study this after database.js to understand how user data is structured and validated.",
      "architectural_layer": "Data Model",
      "complexity_score": 52,
      "dependency_radius": 1
    }
  ],
  "constellation_graph": {
    "nodes": [
      {
        "id": "src_config_database_js",
        "label": "database.js",
        "group": "database_layer",
        "file_path": "src/config/database.js",
        "complexity": 45,
        "importance": 85,
        "incoming_deps": 14,
        "outgoing_deps": 0
      }
    ],
    "edges": [
      {
        "from": "src_models_user_js",
        "to": "src_config_database_js",
        "relationship": "imports"
      }
    ]
  },
  "summary": {
    "total_files": 45,
    "total_dependencies": 120,
    "circular_dependencies": 2,
    "architectural_layers": {
      "Configuration": 3,
      "Foundation": 5,
      "Data Model": 8,
      "Database Layer": 4,
      "Business Logic": 12,
      "API Layer": 8,
      "UI Layer": 5
    },
    "foundational_files": [
      "src/config/database.js",
      "src/config/env.js",
      "src/utils/logger.js"
    ],
    "hub_files": [
      "src/models/user.js",
      "src/services/auth.js"
    ],
    "risky_files": [
      "src/services/payment.js",
      "src/controllers/admin.js"
    ]
  }
}
```

## Data Flow Details

### Step 1: Repository Parsing

```python
# In orchestration.py
from engine.dependency_intelligence import build_dependency_intelligence

intelligence = build_dependency_intelligence(repo_path, include_tests=False)
# Returns: DependencyIntelligencePayload with complete analysis
```

### Step 2: Extract Critical Files

```python
# Sort by importance score
critical_files = sorted(
    intelligence.nodes,
    key=lambda n: n.importance_score,
    reverse=True
)[:10]
```

### Step 3: Generate AI Explanations

```python
# For each critical file
from bob_core.bob_service import generate_explanation

file_context = f"""
File: {file_path}
Layer: {architectural_layer}
Complexity: {complexity_score}/100
Dependencies: {len(prerequisites)}
"""

explanation = await generate_explanation(file_context, task_description)
```

### Step 4: Build Learning Roadmap

```python
roadmap_items = []
for roadmap_item in intelligence.roadmap[:max_files]:
    roadmap_items.append({
        "step": roadmap_item.step,
        "file_path": roadmap_item.file,
        "dependencies_count": len(roadmap_item.prerequisites),
        "priority": calculate_priority(node),
        "bob_explanation": explanation,
        "architectural_layer": roadmap_item.architectural_layer,
        "complexity_score": roadmap_item.complexity_score,
        "dependency_radius": roadmap_item.dependency_radius
    })
```

### Step 5: Format for Frontend

```python
from bob_core.response_formatter import format_compass_response

formatted = format_compass_response(result)
# Returns exact JSON structure for Ali Jan's frontend
```

## Testing the Integration

### Unit Test Example

```python
import pytest
from bob_core.orchestration import CompassOrchestrator

@pytest.mark.asyncio
async def test_complete_analysis():
    orchestrator = CompassOrchestrator(
        repo_path="./test_repo",
        include_tests=False
    )
    
    result = await orchestrator.generate_complete_analysis(
        max_roadmap_files=5,
        task_description="Test analysis"
    )
    
    assert result["status"] == "success"
    assert "learning_roadmap" in result
    assert "constellation_graph" in result
    assert len(result["learning_roadmap"]) <= 5
```

### Integration Test

```bash
# Test with a real repository
python -c "
import asyncio
from bob_core.orchestration import analyze_repository_for_compass

async def test():
    result = await analyze_repository_for_compass(
        repo_path='./navigator_ui',
        max_roadmap_files=10
    )
    print(f'Analyzed {result[\"summary\"][\"total_files\"]} files')
    print(f'Dependency score: {result[\"dependency_radius_score\"]}')

asyncio.run(test())
"
```

## Environment Variables

Make sure these are set in your `.env` file:

```bash
IBM_CLOUD_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
MODEL_ID=ibm/granite-3-8b-instruct
```

## Troubleshooting

### Issue: "Repository path does not exist"
**Solution**: Ensure the `repo_path` is an absolute path or relative to the working directory where FastAPI is running.

### Issue: "Failed to generate explanation"
**Solution**: Check IBM Cloud API credentials in `.env` file. The system will fall back to basic explanations if AI fails.

### Issue: "Token limit exceeded"
**Solution**: The chunking service automatically handles this, but you can reduce `max_roadmap_files` to analyze fewer files.

### Issue: Type errors in orchestration.py
**Solution**: These are expected Optional type warnings from the type checker. The code handles None cases properly at runtime.

## Next Steps for Ali Jan (Frontend)

1. **Call the endpoint**: `POST /api/v1/compass/analyze`
2. **Parse the response**: Extract `learning_roadmap` and `constellation_graph`
3. **Render the roadmap**: Display steps in order with Bob's explanations
4. **Visualize the graph**: Use the nodes/edges to create the constellation view
5. **Show the score**: Display `dependency_radius_score` as a complexity indicator

## Summary

The integration is complete! The workflow now:

1. ✅ Parses repositories using `engine/parser.py`
2. ✅ Calculates dependency intelligence using `engine/dependency_intelligence.py`
3. ✅ Chunks files using `bob_core/chunking.py`
4. ✅ Generates AI explanations using `bob_core/bob_service.py`
5. ✅ Formats responses using `bob_core/response_formatter.py`
6. ✅ Orchestrates everything via `bob_core/orchestration.py`
7. ✅ Exposes API endpoint in `bob_core/main.py`

The exact JSON structure Ali Jan needs is now returned from `/api/v1/compass/analyze`.