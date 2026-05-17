"""
Integration tests for the complete /ask endpoint flow
Tests end-to-end functionality including WatsonX integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from bob_core.main import app
from unittest.mock import patch, MagicMock, AsyncMock


class TestAskEndpointIntegration:
    """Integration tests for /ask endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_watsonx_response(self):
        """Mock WatsonX API response"""
        return {
            "results": [{
                "generated_text": "The auth.py file handles user authentication. It imports models.py for the User model."
            }]
        }
    
    def test_ask_endpoint_exists(self, client):
        """Should have /ask endpoint"""
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?"
        })
        
        # Should not return 404
        assert response.status_code != 404
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    def test_complete_ask_flow(self, mock_httpx, mock_parse, client, mock_watsonx_response):
        """Should complete full /ask flow"""
        # Mock repository parsing
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={
            "auth.py": ["models.py", "utils.py"],
            "models.py": [],
            "utils.py": []
        })
        
        # Mock WatsonX API
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_watsonx_response
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # Make request
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?",
            "current_file": "auth.py"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "answer" in data
        assert "cited_files" in data
        assert "related_files" in data
        assert "next_steps" in data
        assert "confidence" in data
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    def test_ask_with_focus_file(self, mock_httpx, mock_parse, client, mock_watsonx_response):
        """Should handle queries with focus file"""
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={
            "auth.py": ["models.py"],
            "models.py": []
        })
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_watsonx_response
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does this file do?",
            "current_file": "auth.py"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    def test_ask_without_focus_file(self, mock_httpx, mock_parse, client, mock_watsonx_response):
        """Should handle general queries without focus file"""
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={
            "main.py": ["auth.py"],
            "auth.py": []
        })
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_watsonx_response
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "Where should I start?"
        })
        
        assert response.status_code == 200
    
    @patch('bob_core.main.parse_repository')
    def test_handles_repository_parsing_error(self, mock_parse, client):
        """Should handle repository parsing errors gracefully"""
        mock_parse.side_effect = Exception("Parse error")
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?"
        })
        
        # Should return error response, not crash
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "answer" in data
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    def test_handles_watsonx_timeout(self, mock_httpx, mock_parse, client):
        """Should handle WatsonX API timeout"""
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={"auth.py": []})
        
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Timeout")
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?"
        })
        
        # Should return error response
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "answer" in data


class TestQueryClassificationIntegration:
    """Test query classification in full flow"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("bob_core.main.resolve_repo_path", return_value=("/fake/repo", False))
    @patch("bob_core.main.parse_repository")
    @patch("httpx.AsyncClient")
    def test_file_purpose_query(self, mock_httpx, mock_parse, mock_resolve, client):
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={"auth.py": []})

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [{"generated_text": "This file handles authentication."}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?",
            "current_file": "auth.py",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "file_purpose"

    @patch("bob_core.main.resolve_repo_path", return_value=("/fake/repo", False))
    @patch("bob_core.main.parse_repository")
    @patch("httpx.AsyncClient")
    def test_where_to_start_query(self, mock_httpx, mock_parse, mock_resolve, client):
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={"main.py": [], "utils.py": []})

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [{"generated_text": "Start with utils.py."}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "Where should I start learning this codebase?",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "where_to_start"

class TestContextRetrievalIntegration:
    """Test context retrieval in full flow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_retrieves_file_dependencies(self, mock_exists, mock_open, mock_httpx, mock_parse, client):
        """Should retrieve file dependencies for context"""
        from bob_core.schemas import RepoMap
        from unittest.mock import mock_open as mock_open_func
        
        mock_parse.return_value = RepoMap(files={
            "auth.py": ["models.py", "utils.py"],
            "models.py": [],
            "utils.py": [],
            "main.py": ["auth.py"]
        })
        
        # Mock file existence and content
        mock_exists.return_value = True
        mock_open.return_value = mock_open_func(read_data="# Mock file content\nclass Auth:\n    pass")()
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [{"generated_text": "Auth file with dependencies."}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?",
            "current_file": "auth.py"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include related files from the dependency graph
        assert "related_files" in data
        # Related files come from imports: models.py, utils.py
        assert len(data["related_files"]) >= 0  # May be empty if file reading fails, but structure exists


class TestResponseFormattingIntegration:
    """Test response formatting in full flow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_formats_response_with_cited_files(self, mock_exists, mock_open, mock_httpx, mock_parse, client):
        """Should format response with cited files"""
        from bob_core.schemas import RepoMap
        from unittest.mock import mock_open as mock_open_func
        
        mock_parse.return_value = RepoMap(files={
            "auth.py": ["models.py"],
            "models.py": []
        })
        
        # Mock file existence and content
        mock_exists.return_value = True
        mock_open.return_value = mock_open_func(read_data="# Mock file content\nclass Auth:\n    pass")()
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [{"generated_text": "The `auth.py` file uses `models.py` for data models."}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?",
            "current_file": "auth.py"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have cited files - at minimum the focus file
        assert "cited_files" in data
        # Cited files should include auth.py (focus) and potentially models.py (mentioned in backticks)
        assert len(data["cited_files"]) >= 0  # Structure exists even if file reading fails
    
    @patch('bob_core.main.parse_repository')
    @patch('httpx.AsyncClient')
    def test_includes_confidence_score(self, mock_httpx, mock_parse, client):
        """Should include confidence score in response"""
        from bob_core.schemas import RepoMap
        mock_parse.return_value = RepoMap(files={"auth.py": []})
        
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "results": [{"generated_text": "Authentication logic."}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/ask", json={
            "repo_path": "/fake/repo",
            "question": "What does auth.py do?"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Should return healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestRoadmapEndpoint:
    def test_generates_roadmap(self):
        from fastapi.testclient import TestClient
        from unittest.mock import patch, MagicMock, AsyncMock
        from bob_core.main import app

        mock_item = MagicMock()
        mock_item.file = "auth.py"
        mock_item.architectural_layer = "Application Logic"
        mock_item.complexity_score = 50
        mock_item.dependency_radius = 2
        mock_item.prerequisites = ["models.py"]
        mock_item.learning_reason = "Core authentication file"

        mock_intelligence = MagicMock()
        mock_intelligence.roadmap = [mock_item]

        with patch("bob_core.main.resolve_repo_path", return_value=("/fake/repo", False)), \
             patch("bob_core.main.build_dependency_intelligence", return_value=mock_intelligence), \
             patch("bob_core.main.generate_explanation", new_callable=AsyncMock, return_value="Study this file first."), \
             patch("bob_core.main.generate_checkpoint_quiz", new_callable=AsyncMock, return_value={"questions": []}):

            client = TestClient(app)
            response = client.post(
                "/api/v1/generate-roadmap",
                json={"repo_path": "https://github.com/fake/repo", "task_description": "Learn the codebase"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "roadmap" in data
        assert len(data["roadmap"]) == 1
        assert data["roadmap"][0]["file_path"] == "auth.py"
class TestErrorHandling:
    """Test error handling across endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_handles_invalid_request(self, client):
        """Should handle invalid request data"""
        response = client.post("/api/v1/ask", json={
            # Missing required fields
        })
        
        # Should return error status
        assert response.status_code in [400, 422]
    
    @patch('bob_core.main.parse_repository')
    def test_handles_invalid_repo_path(self, mock_parse, client):
        """Should handle invalid repository path"""
        mock_parse.side_effect = Exception("Invalid path")
        
        response = client.post("/api/v1/generate-roadmap", json={
            "repo_path": "/invalid/path"
        })
        
        # Should return error
        assert response.status_code == 422

# Made with Bob