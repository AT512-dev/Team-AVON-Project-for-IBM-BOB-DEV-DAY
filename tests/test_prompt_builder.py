"""
Tests for prompt builder functionality
Following TDD principles: test behaviors, not implementation
"""

import pytest
from bob_core.prompts import (
    build_mentor_prompt,
    classify_query,
    format_repo_structure,
    format_ranked_files
)


class TestQueryClassification:
    """Test query classification logic"""
    
    def test_classifies_file_purpose_queries(self):
        """Should identify file purpose questions"""
        questions = [
            "What does auth.py do?",
            "What is the purpose of models.py?",
            "What is the role of utils.py?"
        ]
        for question in questions:
            assert classify_query(question) == "file_purpose"
    
    def test_classifies_where_to_start_queries(self):
        """Should identify where to start questions"""
        questions = [
            "Where should I start?",
            "Where to begin learning this codebase?",
            "What file should I start with?"
        ]
        for question in questions:
            assert classify_query(question) == "where_to_start"
    
    def test_classifies_impact_analysis_queries(self):
        """Should identify impact analysis questions"""
        questions = [
            "What breaks if I modify auth.py?",
            "What's the impact of changing this file?",
            "What if I change the database connection?"
        ]
        for question in questions:
            assert classify_query(question) == "impact_analysis"
    
    def test_defaults_to_general_for_unknown_queries(self):
        """Should default to general for unrecognized patterns"""
        question = "Tell me about the architecture"
        assert classify_query(question) == "general"


class TestPromptBuilder:
    """Test prompt building functionality"""
    
    def test_builds_prompt_with_base_persona(self):
        """Should include base mentor persona in all prompts"""
        repo_context = {"name": "test-repo", "files": {}}
        prompt = build_mentor_prompt(
            query_type="general",
            repo_context=repo_context,
            user_question="What is this project?"
        )
        
        assert "senior technical mentor" in prompt.lower()
        assert "test-repo" in prompt
    
    def test_builds_file_purpose_prompt_with_context(self):
        """Should include file context for file_purpose queries"""
        repo_context = {"name": "test-repo", "files": {"auth.py": ["models.py"]}}
        prompt = build_mentor_prompt(
            query_type="file_purpose",
            repo_context=repo_context,
            user_question="What does auth.py do?",
            file_path="auth.py",
            imports=["models.py", "utils.py"],
            imported_by=["main.py"],
            complexity="Medium"
        )
        
        assert "auth.py" in prompt
        assert "models.py" in prompt
        assert "main.py" in prompt
        assert "Medium" in prompt
    
    def test_builds_where_to_start_prompt_with_ranked_files(self):
        """Should include ranked files for where_to_start queries"""
        repo_context = {"name": "test-repo", "files": {}}
        ranked_files = "1. utils.py (Easy)\n2. models.py (Medium)"
        
        prompt = build_mentor_prompt(
            query_type="where_to_start",
            repo_context=repo_context,
            user_question="Where should I start?",
            ranked_files=ranked_files
        )
        
        assert "utils.py" in prompt
        assert "models.py" in prompt
    
    def test_handles_missing_optional_parameters(self):
        """Should handle missing optional parameters gracefully"""
        repo_context = {"name": "test-repo", "files": {}}
        
        # Should not raise exception
        prompt = build_mentor_prompt(
            query_type="file_purpose",
            repo_context=repo_context,
            user_question="What does auth.py do?"
        )
        
        assert prompt is not None
        assert len(prompt) > 0


class TestRepoStructureFormatter:
    """Test repository structure formatting"""
    
    def test_formats_repo_structure_with_files(self):
        """Should format repository structure summary"""
        repo_context = {
            "name": "test-repo",
            "files": {
                "main.py": ["utils.py", "models.py"],
                "utils.py": [],
                "models.py": ["database.py"]
            }
        }
        
        formatted = format_repo_structure(repo_context)
        
        assert "Total files: 3" in formatted
        assert "main.py" in formatted
    
    def test_handles_empty_repo(self):
        """Should handle empty repository gracefully"""
        repo_context = {"name": "empty-repo", "files": {}}
        
        formatted = format_repo_structure(repo_context)
        
        assert "not available" in formatted.lower()
    
    def test_limits_file_list_to_ten(self):
        """Should limit displayed files to 10"""
        files = {f"file{i}.py": [] for i in range(20)}
        repo_context = {"name": "large-repo", "files": files}
        
        formatted = format_repo_structure(repo_context)
        
        assert "20" in formatted  # Total count
        assert "10 more files" in formatted  # Indicates truncation


class TestRankedFilesFormatter:
    """Test ranked files formatting"""
    
    def test_formats_ranked_files_list(self):
        """Should format ranked files with scores"""
        files_with_scores = [
            {"file_path": "utils.py", "complexity": "Easy", "centrality": 0.8},
            {"file_path": "models.py", "complexity": "Medium", "centrality": 0.6}
        ]
        
        formatted = format_ranked_files(files_with_scores)
        
        assert "1. utils.py" in formatted
        assert "Easy" in formatted
        assert "0.80" in formatted
        assert "2. models.py" in formatted
    
    def test_handles_empty_file_list(self):
        """Should handle empty file list"""
        formatted = format_ranked_files([])
        
        assert "No files available" in formatted
    
    def test_limits_to_ten_files(self):
        """Should limit output to 10 files"""
        files = [
            {"file_path": f"file{i}.py", "complexity": "Easy", "centrality": 0.5}
            for i in range(20)
        ]
        
        formatted = format_ranked_files(files)
        
        # Should only show first 10
        assert "file9.py" in formatted
        assert "file10.py" not in formatted


class TestPromptIntegration:
    """Integration tests for complete prompt building"""
    
    def test_complete_file_purpose_workflow(self):
        """Should build complete prompt for file purpose query"""
        question = "What does auth.py do?"
        query_type = classify_query(question)
        
        repo_context = {
            "name": "my-app",
            "files": {
                "auth.py": ["models.py", "utils.py"],
                "models.py": [],
                "utils.py": []
            }
        }
        
        prompt = build_mentor_prompt(
            query_type=query_type,
            repo_context=repo_context,
            user_question=question,
            file_path="auth.py",
            imports=["models.py", "utils.py"],
            imported_by=["main.py"],
            complexity="Medium"
        )
        
        # Verify all key components are present
        assert "senior technical mentor" in prompt.lower()
        assert "my-app" in prompt
        assert "auth.py" in prompt
        assert "models.py" in prompt
        assert "Medium" in prompt
        assert question in prompt
    
    def test_complete_where_to_start_workflow(self):
        """Should build complete prompt for where to start query"""
        question = "Where should I start learning this codebase?"
        query_type = classify_query(question)
        
        repo_context = {
            "name": "my-app",
            "files": {"utils.py": [], "models.py": [], "main.py": []}
        }
        
        ranked = format_ranked_files([
            {"file_path": "utils.py", "complexity": "Easy", "centrality": 0.3},
            {"file_path": "models.py", "complexity": "Medium", "centrality": 0.6}
        ])
        
        prompt = build_mentor_prompt(
            query_type=query_type,
            repo_context=repo_context,
            user_question=question,
            ranked_files=ranked
        )
        
        assert "where_to_start" in query_type
        assert "utils.py" in prompt
        assert "Easy" in prompt

# Made with Bob
