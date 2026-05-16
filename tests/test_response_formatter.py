"""
Tests for response formatter functionality
Following TDD principles: test behaviors, not implementation
"""

import pytest
from bob_core.response_formatter import (
    format_mentor_response,
    extract_cited_files,
    extract_next_steps,
    get_related_files,
    calculate_confidence,
    format_error_response,
    find_file_in_context
)
from bob_core.context_service import FileContext


class TestResponseFormatting:
    """Test response formatting"""
    
    def test_formats_complete_response(self):
        """Should format complete response with all fields"""
        raw_response = "The `auth.py` file handles authentication. Check `models.py` for user schema."
        context = {
            "focus": FileContext(
                path="auth.py",
                content="# auth content",
                imports=["models.py"],
                imported_by=["main.py"],
                complexity="Medium",
                loc=50
            ),
            "related": []
        }
        
        formatted = format_mentor_response(raw_response, context, "file_purpose")
        
        assert "answer" in formatted
        assert "cited_files" in formatted
        assert "related_files" in formatted
        assert "next_steps" in formatted
        assert "confidence" in formatted
        assert "query_type" in formatted
        assert formatted["query_type"] == "file_purpose"
    
    def test_includes_raw_answer(self):
        """Should include raw answer text"""
        raw_response = "This is the answer."
        context = {"focus": None, "related": []}
        
        formatted = format_mentor_response(raw_response, context, "general")
        
        assert formatted["answer"] == "This is the answer."


class TestCitedFileExtraction:
    """Test cited file extraction"""
    
    def test_extracts_files_in_backticks(self):
        """Should extract files mentioned in backticks"""
        raw_response = "Check `auth.py` and `models.py` for details."
        context = {"focus": None, "related": []}
        
        cited = extract_cited_files(raw_response, context)
        
        # Should find mentioned files
        assert len(cited) > 0
    
    def test_includes_focus_file_first(self):
        """Should include focus file as first cited file"""
        raw_response = "The file handles authentication."
        context = {
            "focus": FileContext(
                path="auth.py",
                content="",
                imports=[],
                imported_by=[],
                complexity="Medium",
                loc=50
            ),
            "related": []
        }
        
        cited = extract_cited_files(raw_response, context)
        
        assert len(cited) > 0
        assert cited[0]["path"] == "auth.py"
        assert cited[0]["reason"] == "Primary file in question"
    
    def test_includes_related_files(self):
        """Should include related files from context"""
        raw_response = "The file works with dependencies."
        context = {
            "focus": None,
            "related": [
                FileContext("models.py", "", [], [], "Easy", 30),
                FileContext("utils.py", "", [], [], "Easy", 20)
            ]
        }
        
        cited = extract_cited_files(raw_response, context)
        
        assert len(cited) > 0
        assert any(f["path"] == "models.py" for f in cited)
    
    def test_deduplicates_cited_files(self):
        """Should not duplicate files in cited list"""
        raw_response = "Check `auth.py` and `auth.py` again."
        context = {
            "focus": FileContext("auth.py", "", [], [], "Medium", 50),
            "related": []
        }
        
        cited = extract_cited_files(raw_response, context)
        
        # Should only have auth.py once
        auth_files = [f for f in cited if f["path"] == "auth.py"]
        assert len(auth_files) == 1


class TestNextStepsExtraction:
    """Test next steps extraction"""
    
    def test_extracts_explicit_next_steps(self):
        """Should extract explicit next step recommendations"""
        raw_response = "Start by studying models.py. Next, check utils.py for helpers."
        
        steps = extract_next_steps(raw_response)
        
        assert len(steps) > 0
        assert any("models.py" in step for step in steps)
    
    def test_extracts_recommendation_patterns(self):
        """Should extract various recommendation patterns"""
        raw_response = "You should review auth.py first. I recommend checking models.py next."
        
        steps = extract_next_steps(raw_response)
        
        assert len(steps) > 0
    
    def test_limits_number_of_steps(self):
        """Should limit to 5 steps maximum"""
        raw_response = " ".join([f"Step {i}: check file{i}.py." for i in range(10)])
        
        steps = extract_next_steps(raw_response)
        
        assert len(steps) <= 5
    
    def test_handles_no_explicit_steps(self):
        """Should handle responses without explicit steps"""
        raw_response = "This file handles authentication logic."
        
        steps = extract_next_steps(raw_response)
        
        # Should return empty list or extract implicit steps
        assert isinstance(steps, list)


class TestRelatedFilesExtraction:
    """Test related files extraction"""
    
    def test_gets_related_from_focus_file(self):
        """Should get related files from focus file dependencies"""
        context = {
            "focus": FileContext(
                path="auth.py",
                content="",
                imports=["models.py", "utils.py"],
                imported_by=["main.py"],
                complexity="Medium",
                loc=50
            ),
            "related": []
        }
        
        related = get_related_files(context)
        
        assert "models.py" in related
        assert "utils.py" in related
        assert "main.py" in related
    
    def test_gets_related_from_context(self):
        """Should get related files from context"""
        context = {
            "focus": None,
            "related": [
                FileContext("models.py", "", [], [], "Easy", 30),
                FileContext("utils.py", "", [], [], "Easy", 20)
            ]
        }
        
        related = get_related_files(context)
        
        assert "models.py" in related
        assert "utils.py" in related
    
    def test_deduplicates_related_files(self):
        """Should deduplicate related files"""
        context = {
            "focus": FileContext("auth.py", "", ["models.py"], ["models.py"], "Medium", 50),
            "related": [FileContext("models.py", "", [], [], "Easy", 30)]
        }
        
        related = get_related_files(context)
        
        # models.py should appear only once
        assert related.count("models.py") == 1
    
    def test_limits_to_ten_files(self):
        """Should limit to 10 related files"""
        context = {
            "focus": None,
            "related": [
                FileContext(f"file{i}.py", "", [], [], "Easy", 10)
                for i in range(20)
            ]
        }
        
        related = get_related_files(context)
        
        assert len(related) <= 10


class TestConfidenceCalculation:
    """Test confidence score calculation"""
    
    def test_base_confidence_without_context(self):
        """Should have base confidence without context"""
        context = {"focus": None, "related": []}
        cited_files = []
        
        confidence = calculate_confidence(context, cited_files)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence == 0.5  # Base confidence
    
    def test_increases_with_focus_file(self):
        """Should increase confidence with focus file"""
        context_without = {"focus": None, "related": []}
        context_with = {
            "focus": FileContext("auth.py", "", [], [], "Medium", 50),
            "related": []
        }
        
        conf_without = calculate_confidence(context_without, [])
        conf_with = calculate_confidence(context_with, [])
        
        assert conf_with > conf_without
    
    def test_increases_with_related_files(self):
        """Should increase confidence with related files"""
        context = {
            "focus": None,
            "related": [
                FileContext("models.py", "", [], [], "Easy", 30),
                FileContext("utils.py", "", [], [], "Easy", 20)
            ]
        }
        
        confidence = calculate_confidence(context, [])
        
        assert confidence > 0.5
    
    def test_increases_with_cited_files(self):
        """Should increase confidence with cited files"""
        context = {"focus": None, "related": []}
        cited_files = [
            {"path": "auth.py", "reason": "mentioned"},
            {"path": "models.py", "reason": "mentioned"}
        ]
        
        confidence = calculate_confidence(context, cited_files)
        
        assert confidence > 0.5
    
    def test_caps_at_95_percent(self):
        """Should cap confidence at 0.95"""
        context = {
            "focus": FileContext("auth.py", "", [], [], "Medium", 50),
            "related": [FileContext(f"file{i}.py", "", [], [], "Easy", 10) for i in range(10)]
        }
        cited_files = [{"path": f"file{i}.py", "reason": "test"} for i in range(10)]
        
        confidence = calculate_confidence(context, cited_files)
        
        assert confidence <= 0.95


class TestErrorResponseFormatting:
    """Test error response formatting"""
    
    def test_formats_error_response(self):
        """Should format error response with helpful message"""
        error_msg = "Repository not found"
        
        response = format_error_response(error_msg, "general")
        
        assert "error" in response
        assert response["error"] is True
        assert error_msg in response["answer"]
        assert response["confidence"] == 0.0
    
    def test_includes_helpful_next_steps(self):
        """Should include helpful next steps in error response"""
        response = format_error_response("Some error", "general")
        
        assert len(response["next_steps"]) > 0
        assert any("repository path" in step.lower() for step in response["next_steps"])
    
    def test_preserves_query_type(self):
        """Should preserve query type in error response"""
        response = format_error_response("Error", "file_purpose")
        
        assert response["query_type"] == "file_purpose"


class TestFileInContextFinder:
    """Test finding files in context"""
    
    def test_finds_file_in_focus(self):
        """Should find file in focus context"""
        context = {
            "focus": FileContext("auth.py", "", [], [], "Medium", 50),
            "related": []
        }
        
        file_info = find_file_in_context("auth.py", context)
        
        assert file_info is not None
        assert file_info["path"] == "auth.py"
        assert file_info["complexity"] == "Medium"
    
    def test_finds_file_in_related(self):
        """Should find file in related files"""
        context = {
            "focus": None,
            "related": [
                FileContext("models.py", "", [], [], "Easy", 30)
            ]
        }
        
        file_info = find_file_in_context("models.py", context)
        
        assert file_info is not None
        assert file_info["path"] == "models.py"
    
    def test_returns_basic_info_for_unknown_file(self):
        """Should return basic info for files not in context"""
        context = {"focus": None, "related": []}
        
        file_info = find_file_in_context("unknown.py", context)
        
        assert file_info is not None
        assert file_info["path"] == "unknown.py"
        assert file_info["complexity"] == "Unknown"


class TestResponseIntegration:
    """Integration tests for complete response formatting"""
    
    def test_complete_response_workflow(self):
        """Should format complete response with all components"""
        raw_response = """The `auth.py` file handles user authentication. 
        It imports `models.py` for the User model and `utils.py` for token generation.
        Start by reviewing the authenticate_user function. Next, check the token validation logic."""
        
        context = {
            "focus": FileContext(
                path="auth.py",
                content="# auth content",
                imports=["models.py", "utils.py"],
                imported_by=["main.py", "router.py"],
                complexity="Medium",
                loc=150
            ),
            "related": [
                FileContext("models.py", "", [], [], "Easy", 50),
                FileContext("utils.py", "", [], [], "Easy", 30)
            ]
        }
        
        formatted = format_mentor_response(raw_response, context, "file_purpose")
        
        # Verify all components
        assert formatted["answer"] == raw_response
        assert len(formatted["cited_files"]) > 0
        assert "auth.py" in [f["path"] for f in formatted["cited_files"]]
        assert len(formatted["related_files"]) > 0
        assert len(formatted["next_steps"]) > 0
        assert 0.0 < formatted["confidence"] < 1.0
        assert formatted["query_type"] == "file_purpose"

# Made with Bob