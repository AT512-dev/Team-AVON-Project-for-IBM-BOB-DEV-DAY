# GitHub URL Integration - Backend Implementation

## Overview
The backend has been successfully updated to accept GitHub URLs from the frontend instead of local file paths. The system now automatically clones repositories to temporary directories, processes them, and cleans up afterward.

## Changes Made

### 1. New Git Utilities Module (`bob_core/git_utils.py`)
Created a comprehensive utility module for handling GitHub repository operations:

- **`clone_github_repo(github_url: str)`**: Clones a GitHub repository to a temporary directory
  - Validates GitHub URLs
  - Creates temporary directories with unique names
  - Performs shallow clone (depth=1) for efficiency
  - Returns tuple of (temp_path, repo_name)
  - Handles errors with custom `GitCloneError` exception

- **`cleanup_temp_repo(repo_path: str)`**: Cleans up temporary directories
  - Handles Windows read-only file issues (common with .git directories)
  - Only deletes directories matching our naming pattern for safety
  - Returns success/failure status

- **`is_valid_github_url(url: str)`**: Validates GitHub URLs
  - Checks for proper format and GitHub domain

### 2. Updated API Models (`bob_core/main.py`)
Changed all Pydantic request models to accept `github_url` instead of `repo_path`:

**Before:**
```python
class OnboardRequest(BaseModel):
    repo_path: str
    task_description: Optional[str]
```

**After:**
```python
class OnboardRequest(BaseModel):
    github_url: str
    task_description: Optional[str]
```

This change applies to:
- `OnboardRequest`
- `CompassAnalysisRequest`
- `AskRequest`

### 3. Updated API Endpoints
All three main endpoints now follow this pattern:

1. Validate the GitHub URL
2. Clone the repository to a temporary directory
3. Process the cloned repository
4. Return results
5. **Always** cleanup the temporary directory (in `finally` block)

**Endpoints Updated:**
- `/api/v1/generate-roadmap`
- `/api/v1/compass/analyze`
- `/api/v1/ask`

### 4. Error Handling
Comprehensive error handling for:
- Invalid GitHub URLs (400 Bad Request)
- Clone failures (422 Unprocessable Entity)
- Repository parsing errors (422 Unprocessable Entity)
- General processing errors (500 Internal Server Error)

## Frontend Integration

### Request Format
The frontend should now send requests with `github_url` parameter:

```typescript
// Example: Compass Analysis Request
const response = await fetch('http://localhost:8000/api/v1/compass/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    github_url: 'https://github.com/user/repository',
    task_description: 'Understand the codebase architecture',
    max_roadmap_files: 10,
    include_tests: false
  })
});
```

### All Endpoints Accept GitHub URLs

1. **Generate Roadmap**
   ```json
   POST /api/v1/generate-roadmap
   {
     "github_url": "https://github.com/user/repo",
     "task_description": "optional description"
   }
   ```

2. **Compass Analysis**
   ```json
   POST /api/v1/compass/analyze
   {
     "github_url": "https://github.com/user/repo",
     "task_description": "optional description",
     "max_roadmap_files": 10,
     "include_tests": false
   }
   ```

3. **Ask Bob**
   ```json
   POST /api/v1/ask
   {
     "github_url": "https://github.com/user/repo",
     "question": "What does this code do?",
     "current_file": "optional/file/path.js"
   }
   ```

## Testing

A comprehensive test suite has been created (`test_github_integration.py`) that verifies:

- ✅ URL validation (valid and invalid URLs)
- ✅ Repository cloning (using public GitHub repo)
- ✅ Temporary directory cleanup (including Windows read-only files)
- ✅ Error handling for non-existent repositories
- ✅ API request model format validation

**Run tests:**
```bash
python Team-AVON-Project-for-IBM-BOB-DEV-DAY/test_github_integration.py
```

**Test Results:**
```
============================================================
[SUCCESS] All tests passed!
============================================================

Backend is ready to accept GitHub URLs from the frontend.
Frontend should send requests with 'github_url' parameter.
```

## Key Features

### 1. Automatic Cleanup
- Temporary directories are **always** cleaned up, even if processing fails
- Uses `finally` blocks to ensure cleanup happens
- Handles Windows-specific file permission issues

### 2. Security
- Only clones from GitHub (validates domain)
- Uses shallow clones (depth=1) to minimize data transfer
- Temporary directories use unique names to prevent conflicts
- Only deletes directories matching our naming pattern

### 3. Performance
- Shallow clones reduce clone time and disk usage
- Temporary directories are created in system temp location
- Automatic cleanup prevents disk space accumulation

### 4. Error Messages
Clear, actionable error messages for:
- Invalid URLs
- Clone failures
- Repository not found
- Parsing errors

## Migration Notes

### For Ali (Frontend Developer)
- **Change Required**: Update all API calls to use `github_url` instead of `repo_path`
- **No File Upload Needed**: Frontend only needs to pass the GitHub URL string
- **Example**: `{ "github_url": "https://github.com/user/repo" }`

### For Harshal (Backend Developer)
- **Status**: ✅ Complete - Backend is ready
- **Testing**: All tests passing
- **Deployment**: Ready to deploy

## Example Usage

```python
# The backend now handles everything automatically:

# 1. Frontend sends GitHub URL
request = {
    "github_url": "https://github.com/facebook/react",
    "task_description": "Understand React architecture"
}

# 2. Backend automatically:
#    - Validates the URL
#    - Clones to temp directory
#    - Parses the repository
#    - Generates analysis
#    - Cleans up temp directory
#    - Returns results

# 3. Frontend receives the analysis results
```

## Dependencies

The implementation uses only Python standard library modules:
- `os` - File system operations
- `tempfile` - Temporary directory creation
- `shutil` - Directory removal
- `subprocess` - Git command execution
- `pathlib` - Path manipulation

**No additional packages required!**

## Conclusion

✅ Backend is fully implemented and tested
✅ All endpoints accept GitHub URLs
✅ Automatic cloning and cleanup working
✅ Comprehensive error handling in place
✅ Ready for frontend integration

The backend is now ready to receive GitHub URLs from Ali's frontend. No local file handling is needed on the frontend side.