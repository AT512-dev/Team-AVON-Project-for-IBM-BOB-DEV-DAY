# Backend Integration Guide

## Overview

The Compass AI frontend now supports **real-time backend integration** with automatic fallback to mock data if the backend is unavailable.

---

## 🚀 Quick Start

### 1. Start the Backend (FastAPI)

```bash
# From the project root directory
cd ..
python -m uvicorn bob_core.main:app --reload --port 8000
```

The backend will start at: `http://localhost:8000`

### 2. Start the Frontend (Next.js)

```bash
# From the navigator_ui directory
npm run dev
```

The frontend will start at: `http://localhost:3001`

### 3. Verify Connection

- Open `http://localhost:3001` in your browser
- Check the browser console for connection status:
  - ✅ "Backend connected successfully" = Using real data
  - ⚠️ "Backend not available, using mock data" = Using fallback data

---

## 📡 API Endpoints Used

The frontend connects to these backend endpoints:

### 1. Health Check

```
GET /health
```

Checks if backend is available.

### 2. Dependency Intelligence

```
POST /api/v1/dependency-intelligence
Body: {
  "repo_path": "./",
  "include_tests": false
}
```

Returns full repository analysis with nodes, edges, and roadmap.

### 3. Generate Roadmap

```
POST /api/v1/generate-roadmap
Body: {
  "repo_path": "./",
  "task_description": "Understand the codebase architecture"
}
```

Returns personalized learning roadmap with IBM WatsonX explanations.

### 4. Repository Map

```
GET /api/v1/repo-map?repo_path=./
```

Returns file structure of the repository.

---

## ⚙️ Configuration

### Environment Variables

Create or update `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Repository path for analysis
NEXT_PUBLIC_REPO_PATH=E:/team-avon/Team-AVON-Project-for-IBM-BOB-DEV-DAY
```

**Important:** Update `NEXT_PUBLIC_REPO_PATH` to your actual repository path.

---

## 🔄 How It Works

### Automatic Backend Detection

1. **On Page Load:**
   - Frontend calls `/health` endpoint
   - If successful → loads real data from backend
   - If fails → uses mock data for demo

2. **Data Transformation:**
   - Backend returns `DependencyNode[]` and `DependencyEdge[]`
   - Frontend transforms to `ConstellationNode[]` and `ConstellationEdge[]`
   - Modules are grouped by `architectural_layer`

3. **Fallback Strategy:**
   - Always graceful degradation
   - Mock data ensures demo works without backend
   - Console logs show which data source is active

### Data Flow

```
Backend (FastAPI)
    ↓
/api/v1/dependency-intelligence
    ↓
lib/api.ts (fetch & transform)
    ↓
app/page.tsx (state management)
    ↓
Components (visualization)
```

---

## 🧪 Testing Backend Integration

### Test 1: Backend Available

```bash
# Terminal 1: Start backend
python -m uvicorn bob_core.main:app --reload --port 8000

# Terminal 2: Start frontend
cd navigator_ui
npm run dev

# Browser: Open http://localhost:3001
# Console should show: "✅ Backend connected successfully"
```

### Test 2: Backend Unavailable

```bash
# Terminal 1: Stop backend (Ctrl+C)

# Terminal 2: Frontend still running
# Browser: Refresh http://localhost:3001
# Console should show: "⚠️ Backend not available, using mock data"
```

### Test 3: Analyze Button

```bash
# With backend running:
# Click "Analyze with IBM Bob" button
# Should trigger new API call and reload data
```

---

## 📊 Data Transformation Examples

### Backend Node → Frontend Node

**Backend:**

```json
{
  "id": "auth_middleware_js",
  "file": "src/auth/middleware.js",
  "label": "middleware.js",
  "complexity_score": 8,
  "architectural_layer": "AUTH",
  "recommended_learning_order": 1,
  "dependencies": ["jwt.js", "config.js"]
}
```

**Frontend:**

```typescript
{
  id: "auth_middleware_js",
  fileName: "middleware.js",
  position: { x: 450, y: 320 },
  color: "yellow", // current file
  dependencies: ["jwt.js", "config.js"]
}
```

### Backend Roadmap → Frontend Levels

**Backend:**

```json
{
  "step": 1,
  "file": "src/auth/jwt.ts",
  "complexity_score": 5,
  "learning_reason": "Foundation for authentication"
}
```

**Frontend:**

```typescript
{
  id: "level-1",
  level: 1,
  fileName: "jwt.ts",
  description: "Foundation for authentication",
  difficulty: "MED",
  isCompleted: false
}
```

---

## 🐛 Troubleshooting

### Issue: "Backend not available"

**Solution:**

1. Check if backend is running: `curl http://localhost:8000/health`
2. Verify port 8000 is not in use
3. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`

### Issue: "CORS errors"

**Solution:**
Backend should have CORS middleware enabled. Check `bob_core/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Repository parsing failed"

**Solution:**

1. Verify `NEXT_PUBLIC_REPO_PATH` points to valid directory
2. Check backend has read permissions
3. Ensure repository has parseable code files

---

## 📝 Development Notes

### Mock Data vs Real Data

- **Mock Data:** Hardcoded in `lib/mockData.ts`
  - Always available
  - Fast loading
  - Good for UI development

- **Real Data:** From backend API
  - Requires backend running
  - Slower initial load
  - Reflects actual repository structure

### Adding New API Endpoints

1. Add endpoint to `bob_core/main.py`
2. Add TypeScript types to `lib/api.ts`
3. Add fetch function to `lib/api.ts`
4. Use in `app/page.tsx` or components

---

## 🎯 Production Deployment

For production, update environment variables:

```env
# Production backend URL
NEXT_PUBLIC_API_URL=https://api.compass-ai.com

# Production repo path (or make it user-configurable)
NEXT_PUBLIC_REPO_PATH=/path/to/repo
```

---

## ✅ Integration Checklist

- [x] API client created (`lib/api.ts`)
- [x] Environment variables configured (`.env.local`)
- [x] Health check on mount
- [x] Automatic data loading
- [x] Graceful fallback to mock data
- [x] Loading states and indicators
- [x] Console logging for debugging
- [x] Data transformation functions
- [x] Module grouping by architectural layer
- [ ] Error handling UI (toast notifications)
- [ ] Retry logic for failed requests
- [ ] Caching strategy for API responses

---

**Built by Ali Jan for IBM Bob Hackathon**
