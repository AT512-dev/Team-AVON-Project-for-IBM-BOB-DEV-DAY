# Example Queries - IBM Bob Mentor System

This document provides example questions and expected responses for testing and demonstration purposes.

---

## File Purpose Queries

### Example 1: Understanding a Service File

**Question:** "What does auth.py do?"

**Expected Response Type:** `file_purpose`

**Expected Answer Structure:**
- Explanation of file's primary responsibility
- List of imported dependencies
- List of files that depend on it
- Recommendation on what to study first

**Sample Response:**
```
The `auth.py` file handles user authentication and session management. 
It imports `models.py` for the User schema and `utils.py` for token 
generation helpers. This file is central to the application's security 
layer and is used by `main.py` and `router.py` to protect routes.

Start by understanding the User model in `models.py` first, then review 
the token generation logic in `utils.py` before diving into the 
authentication flows in this file.
```

**Cited Files:**
- `services/auth.py` (Primary file)
- `models.py` (User schema)
- `utils.py` (Token helpers)

---

### Example 2: Understanding a Model File

**Question:** "What is the purpose of models.py?"

**Expected Response Type:** `file_purpose`

**Sample Response:**
```
The `models.py` file defines the data models for the application, 
including User, Session, and Product schemas. It uses SQLAlchemy ORM 
for database mapping and includes validation logic for each model.

This is a foundational file with low complexity - it's imported by 
`auth.py`, `services/user.py`, and `database.py`. Start here to 
understand the data structure before exploring business logic.
```

---

## Where to Start Queries

### Example 3: Beginning a New Codebase

**Question:** "Where should I start learning this codebase?"

**Expected Response Type:** `where_to_start`

**Sample Response:**
```
Based on the repository structure and complexity analysis, I recommend 
this learning path:

1. Start with `utils.py` (Easy) - Helper functions and utilities
2. Then study `models.py` (Easy) - Data models and schemas
3. Next, review `config.py` (Easy) - Configuration and settings
4. Move to `database.py` (Medium) - Database connection logic
5. Finally, explore `services/auth.py` (Medium) - Authentication logic

This order ensures you understand the foundational components before 
tackling more complex business logic.
```

**Cited Files:**
- Ranked list of files with complexity scores
- Entry points highlighted

---

### Example 4: Task-Specific Learning Path

**Question:** "Where should I start to understand the authentication system?"

**Expected Response Type:** `where_to_start`

**Sample Response:**
```
To understand the authentication system, follow this path:

1. `models.py` - Study the User and Session models
2. `utils.py` - Review token generation and validation functions
3. `services/auth.py` - Understand login/logout logic
4. `middleware/auth.py` - See how authentication is enforced
5. `router.py` - Check how protected routes are defined

This path takes you from data structures through business logic to 
implementation, building understanding incrementally.
```

---

## Impact Analysis Queries

### Example 5: Understanding Dependencies

**Question:** "What breaks if I modify auth.py?"

**Expected Response Type:** `impact_analysis`

**Sample Response:**
```
Modifying `auth.py` will directly impact:

**Direct Dependencies (files that import auth.py):**
- `main.py` - Application entry point
- `router.py` - Route definitions
- `middleware/auth.py` - Authentication middleware
- `tests/test_auth.py` - Authentication tests

**Potential Breaking Changes:**
- Changing function signatures will break all callers
- Modifying token format will invalidate existing sessions
- Altering User model interactions may require database migrations

**Recommended Actions:**
1. Review all files in the "Direct Dependencies" list
2. Update corresponding tests
3. Check for any cached authentication data
4. Consider backward compatibility for token changes
```

---

### Example 6: Reverse Dependencies

**Question:** "What depends on models.py?"

**Expected Response Type:** `impact_analysis`

**Sample Response:**
```
The `models.py` file is highly central - 8 files depend on it:

**Direct Importers:**
- `services/auth.py` - Uses User and Session models
- `services/user.py` - User CRUD operations
- `database.py` - Database initialization
- `router.py` - Request/response schemas
- `tests/test_models.py` - Model tests
- `tests/test_auth.py` - Authentication tests
- `tests/test_user.py` - User service tests
- `migrations/env.py` - Database migrations

**Impact of Changes:**
- Schema changes require database migrations
- Adding fields may break existing API contracts
- Removing fields will cause import errors in dependent files

This is a foundational file - changes here have wide-reaching effects.
```

---

## General Queries

### Example 7: Architecture Overview

**Question:** "How does the authentication flow work?"

**Expected Response Type:** `general`

**Sample Response:**
```
The authentication flow follows this pattern:

1. **Login Request** (`router.py`)
   - User submits credentials to `/auth/login`
   - Request validated against User schema

2. **Credential Verification** (`services/auth.py`)
   - Password hashed and compared with stored hash
   - User record retrieved from database

3. **Token Generation** (`utils.py`)
   - JWT token created with user ID and expiration
   - Token signed with secret key

4. **Session Creation** (`services/auth.py`)
   - Session record created in database
   - Token returned to client

5. **Protected Routes** (`middleware/auth.py`)
   - Middleware extracts token from headers
   - Token validated and decoded
   - User context attached to request

Key files: `router.py` → `services/auth.py` → `utils.py` → `middleware/auth.py`
```

---

### Example 8: Design Pattern Inquiry

**Question:** "What design patterns are used in this codebase?"

**Expected Response Type:** `general`

**Sample Response:**
```
This codebase uses several design patterns:

1. **Service Layer Pattern** (`services/` directory)
   - Business logic separated from routes
   - Examples: `auth.py`, `user.py`

2. **Repository Pattern** (`database.py`)
   - Data access abstracted from business logic
   - SQLAlchemy ORM provides the repository interface

3. **Middleware Pattern** (`middleware/` directory)
   - Cross-cutting concerns like authentication
   - Request/response processing pipeline

4. **Dependency Injection** (FastAPI's Depends)
   - Database sessions injected into routes
   - Configuration injected into services

5. **Factory Pattern** (`utils.py`)
   - Token creation and validation functions
   - Configuration object creation

Study `services/auth.py` to see Service Layer pattern in action.
```

---

## Edge Cases

### Example 9: Non-Existent File

**Question:** "What does nonexistent.py do?"

**Expected Response:**
```
I couldn't find `nonexistent.py` in the repository. 

Possible reasons:
- File doesn't exist in the current branch
- File path might be incorrect
- File might be in a subdirectory

Try:
- Checking the file path spelling
- Listing files with: ls -la
- Searching for similar filenames
```

---

### Example 10: Ambiguous Query

**Question:** "Tell me about the code"

**Expected Response Type:** `general`

**Sample Response:**
```
This repository contains a Python web application with the following structure:

**Core Components:**
- `main.py` - Application entry point
- `router.py` - API route definitions
- `services/` - Business logic layer
- `models.py` - Data models

**Key Features:**
- User authentication system
- RESTful API endpoints
- Database integration with SQLAlchemy
- JWT token-based sessions

**Complexity Distribution:**
- Easy: 5 files (utils, models, config)
- Medium: 8 files (services, middleware)
- Hard: 3 files (main, complex services)

For a more specific answer, try asking:
- "Where should I start?"
- "What does [specific file] do?"
- "How does [feature] work?"
```

---

## Performance Test Queries

### Example 11: Large File Query

**Question:** "What does large_service.py do?" (file with 2000+ LOC)

**Expected Behavior:**
- File should be chunked semantically
- Response should focus on relevant sections
- Should mention file is large and complex

**Sample Response:**
```
The `large_service.py` file is a complex service module (2,145 lines) 
that handles multiple responsibilities:

**Main Components:**
1. UserService class (lines 1-500) - User management
2. ProductService class (lines 501-1000) - Product operations
3. OrderService class (lines 1001-1500) - Order processing
4. PaymentService class (lines 1501-2000) - Payment handling
5. Utility functions (lines 2001-2145) - Helper methods

This file is quite large and might benefit from refactoring into 
separate service modules. For now, focus on the specific service 
class relevant to your task.

Which component would you like to explore first?
```

---

## Query Type Classification Examples

| Question | Classified As | Reason |
|----------|---------------|--------|
| "What does auth.py do?" | `file_purpose` | Contains "what does" |
| "What is the role of models.py?" | `file_purpose` | Contains "role" |
| "Where should I start?" | `where_to_start` | Contains "where" + "start" |
| "What breaks if I change this?" | `impact_analysis` | Contains "break" + "change" |
| "How does login work?" | `general` | General architecture question |
| "Explain the database setup" | `general` | Explanation request |

---

## Response Quality Metrics

Good responses should:
- ✅ Cite specific files with backticks
- ✅ Provide actionable next steps
- ✅ Explain relationships between files
- ✅ Use appropriate technical terminology
- ✅ Be concise (2-3 paragraphs)
- ✅ Include complexity indicators

Poor responses:
- ❌ Generic answers without file references
- ❌ Too verbose (>5 paragraphs)
- ❌ No actionable guidance
- ❌ Incorrect file relationships
- ❌ Missing context about dependencies

---

## Testing Checklist

Use these queries to test the system:

- [ ] File purpose query with existing file
- [ ] File purpose query with non-existent file
- [ ] Where to start query (general)
- [ ] Where to start query (task-specific)
- [ ] Impact analysis query
- [ ] Reverse dependency query
- [ ] Architecture overview query
- [ ] Design pattern query
- [ ] Large file query (>1000 LOC)
- [ ] Ambiguous query

---

**Last Updated:** 2026-05-16  
**Version:** 1.0.0  
**Purpose:** Testing and demonstration