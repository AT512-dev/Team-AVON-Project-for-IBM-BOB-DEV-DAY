# Compass AI

Compass AI turns a repository into an onboarding roadmap by analyzing code structure, dependencies, complexity, and architectural learning order.

## Austin/Karl Contribution: Dependency Intelligence Engine

The core intelligence layer lives in `engine/` and provides:

- Repository scanning for Python, JavaScript, TypeScript, React, and Node-style modules.
- File-to-file dependency graph generation.
- Incoming/outgoing dependency counts.
- Circular dependency detection.
- Dependency radius, which measures architectural distance from foundational files.
- Complexity and importance scoring from file size, imports, exports, nesting, coupling, reuse, and graph impact.
- Architectural layer inference such as Configuration, Data Model, Database Layer, Business Logic, API Layer, and UI Layer.
- Recommended learning order for new developer onboarding.
- Visualization-ready nodes and edges for React Flow, D3, Cytoscape, or force graph frontends.

## Run the Engine

```bash
python3 -m engine.run_intelligence /path/to/repository --pretty
```

Example output shape:

```json
{
  "file": "src/authService.ts",
  "complexity_score": 87,
  "dependency_radius": 4,
  "architectural_layer": "Business Logic",
  "recommended_learning_order": 3,
  "dependencies": ["src/database.ts", "src/tokenService.ts"]
}
```

## API Endpoint

```http
POST /api/v1/dependency-intelligence
```

Request:

```json
{
  "repo_path": "/path/to/repository",
  "include_tests": false
}
```

Response includes:

- `summary`: total files, edges, hub files, risky files, foundational files, and cycle count.
- `nodes`: graph-ready file/module intelligence.
- `edges`: directed dependency relationships.
- `roadmap`: ordered learning path with prerequisites and learning reasons.
- `clusters`: architectural layer groupings.
- `circular_dependencies`: cycle paths when detected.
