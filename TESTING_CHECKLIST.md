# 🧪 Compass AI - Testing Checklist

## Pre-Testing Setup

### ✅ Step 1: Start Backend

```bash
cd E:\team-avon\Team-AVON-Project-for-IBM-BOB-DEV-DAY
python -m uvicorn bob_core.main:app --reload --port 8000
```

**Expected:** Backend starts on http://localhost:8000

### ✅ Step 2: Verify Backend Health

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"ok","service":"Compass AI"}`

### ✅ Step 3: Start Frontend

```bash
cd navigator_ui
npm run dev
```

**Expected:** Frontend starts on http://localhost:3001

---

## Browser Testing

### ✅ Initial Load Test

- [ ] Open http://localhost:3001
- [ ] Page loads without errors
- [ ] Loading spinner appears briefly
- [ ] Dashboard displays with three panels

### ✅ Console Check (F12)

Look for these messages:

- [ ] ✅ "Backend connected successfully"
- [ ] 📊 "Loading repository data from: ./"
- [ ] ✅ "Repository data loaded successfully"
- [ ] 📁 "Files: X, Edges: Y"
- [ ] No red errors

### ✅ Visual Components

- [ ] Left panel: Module sidebar visible
- [ ] Left panel: 6 modules listed (AUTH, API, DATABASE, UI, PAYMENTS, ANALYTICS)
- [ ] Left panel: User profile at bottom (Jordan Chen)
- [ ] Center panel: Constellation map visible
- [ ] Center panel: Nodes (stars) visible
- [ ] Center panel: Edges (lines) connecting nodes
- [ ] Center panel: Module labels around map
- [ ] Center panel: Legend at bottom-left
- [ ] Right panel: Bob chat interface
- [ ] Right panel: Welcome message from Bob
- [ ] Top navbar: View toggle buttons (Constellation / Level Map)
- [ ] Top navbar: IBM Bob Connected badge (green)

### ✅ Interaction Tests

#### Module Navigation

- [ ] Click "AUTH" module → view updates
- [ ] Breadcrumb shows "All modules > AUTH"
- [ ] Constellation filters to AUTH files
- [ ] Click "All modules" → returns to full view

#### View Toggle

- [ ] Click "Level Map" button
- [ ] View switches to linear progression
- [ ] Levels displayed vertically
- [ ] Click "Constellation" button
- [ ] View switches back to constellation

#### Constellation Map

- [ ] Drag a node → it moves
- [ ] Zoom in/out with mouse wheel
- [ ] Pan by dragging background
- [ ] Click a node → it highlights
- [ ] Zoom controls work (bottom-right)

#### Level Map

- [ ] Completed levels show green with checkmark
- [ ] Current level shows cyan with glow
- [ ] Locked levels show gray
- [ ] Click completed/current level → highlights

#### Chat Panel

- [ ] Type message in input field
- [ ] Press Enter → message sends
- [ ] User message appears (right-aligned, blue)
- [ ] Typing indicator appears (three dots)
- [ ] Bob response appears after ~1.5s
- [ ] Click suggestion button → sends as message
- [ ] Chat auto-scrolls to latest message

---

## Backend Integration Tests

### ✅ Test 1: With Backend Running

- [ ] Backend is running
- [ ] Frontend loads real data
- [ ] Console shows "Backend connected successfully"
- [ ] Stats show actual file counts
- [ ] Modules reflect real architectural layers

### ✅ Test 2: Without Backend (Fallback)

- [ ] Stop backend (Ctrl+C)
- [ ] Refresh browser
- [ ] Console shows "Backend not available, using mock data"
- [ ] Dashboard still works
- [ ] Mock data displays correctly
- [ ] All interactions still work

### ✅ Test 3: Analyze Button

- [ ] Start backend again
- [ ] Click "Analyze with IBM Bob" button
- [ ] Loading state appears
- [ ] Data reloads from backend
- [ ] View updates with fresh data

---

## Performance Tests

### ✅ Load Time

- [ ] Initial page load < 3 seconds
- [ ] Backend data fetch < 5 seconds
- [ ] View switching < 100ms
- [ ] Node interactions smooth (60fps)

### ✅ Memory

- [ ] No memory leaks after 5 minutes
- [ ] Console shows no warnings
- [ ] Browser doesn't slow down

---

## Cross-Browser Tests (Optional)

### ✅ Chrome

- [ ] All features work
- [ ] No console errors

### ✅ Edge

- [ ] All features work
- [ ] No console errors

### ✅ Firefox

- [ ] All features work
- [ ] No console errors

---

## Error Handling Tests

### ✅ Network Errors

- [ ] Backend crashes → fallback to mock data
- [ ] Backend slow → loading indicator shows
- [ ] Backend returns error → graceful handling

### ✅ Invalid Data

- [ ] Empty repository → shows appropriate message
- [ ] No files found → fallback works

---

## Final Checks

### ✅ Code Quality

- [ ] No ESLint errors
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] Code is formatted

### ✅ Documentation

- [ ] README_BACKEND_INTEGRATION.md is complete
- [ ] TESTING_AND_DEMO_GUIDE.md is up to date
- [ ] Comments in code are clear

### ✅ Git Status

- [ ] All changes staged
- [ ] Commit message ready
- [ ] Ready to push

---

## 🎯 Success Criteria

All checkboxes above should be checked before pushing to GitHub.

**Minimum Requirements:**

- ✅ Dashboard loads without errors
- ✅ Backend integration works
- ✅ Fallback to mock data works
- ✅ All three panels functional
- ✅ Both visualization views work
- ✅ Chat interface functional
- ✅ No critical bugs

---

## 📝 Test Results

**Date:** ********\_********

**Tester:** Ali Jan

**Backend Status:** [ ] Running [ ] Not Running

**Overall Result:** [ ] PASS [ ] FAIL

**Notes:**

---

---

---

---

**Ready for Demo:** [ ] YES [ ] NO

**Ready to Push:** [ ] YES [ ] NO
