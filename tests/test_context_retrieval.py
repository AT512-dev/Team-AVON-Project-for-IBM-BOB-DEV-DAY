"""
Tests for context retrieval service
Following TDD principles: test behaviors, not implementation
"""

import pytest
from unittest.mock import Mock, patch
from bob_core.context_service import ContextRetriever, FileContext
from bob_core.schemas import RepoMap


class TestContextRetrieverInitialization:
    """Test context retriever initialization"""
    
    def test_initializes_with_valid_repo_path(self):
        """Should initialize with valid repository path"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "main.py": ["utils.py"],
                "utils.py": []
            })
            
            retriever = ContextRetriever("/fake/repo/path")
            
            assert retriever.repo_path == "/fake/repo/path"
            assert retriever.repo_map is not None
            mock_parse.assert_called_once_with("/fake/repo/path")
    
    def test_builds_reverse_dependencies(self):
        """Should build reverse dependency map"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "main.py": ["utils.py", "models.py"],
                "utils.py": [],
                "models.py": []
            })
            
            retriever = ContextRetriever("/fake/repo")
            
            # utils.py is imported by main.py
            assert "main.py" in retriever.reverse_deps.get("utils.py", [])
            # models.py is imported by main.py
            assert "main.py" in retriever.reverse_deps.get("models.py", [])
    
    def test_handles_parsing_failure_gracefully(self):
        """Should handle repository parsing failures"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.side_effect = Exception("Parse error")
            
            retriever = ContextRetriever("/fake/repo")
            
            # Should create empty repo map
            assert retriever.repo_map is not None
            assert retriever.repo_map.files == {}


class TestFileContextRetrieval:
    """Test file context retrieval"""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create a mock context retriever"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "auth.py": ["models.py", "utils.py"],
                "models.py": [],
                "utils.py": [],
                "main.py": ["auth.py"]
            })
            
            retriever = ContextRetriever("/fake/repo")
            return retriever
    
    def test_gets_file_context_with_dependencies(self, mock_retriever):
        """Should retrieve file context with imports and imported_by"""
        with patch.object(mock_retriever, '_read_file', return_value="# auth.py content"):
            context = mock_retriever.get_file_context("auth.py")
            
            assert context is not None
            assert context.path == "auth.py"
            assert "models.py" in context.imports
            assert "utils.py" in context.imports
            assert "main.py" in context.imported_by
            # Complexity comes from dependency provider (mock returns "Easy" for files with 2 imports)
            assert context.complexity in ["Easy", "Medium", "Hard"]
    
    def test_returns_none_for_nonexistent_file(self, mock_retriever):
        """Should return None for files not in repository"""
        context = mock_retriever.get_file_context("nonexistent.py")
        
        assert context is None
    
    def test_includes_content_when_requested(self, mock_retriever):
        """Should include file content when include_content=True"""
        with patch.object(mock_retriever, '_read_file', return_value="# File content"):
            with patch('engine.metrics.compute_complexity', return_value="Easy"):
                context = mock_retriever.get_file_context("utils.py", include_content=True)
                
                assert context.content == "# File content"
    
    def test_excludes_content_when_not_requested(self, mock_retriever):
        """Should exclude file content when include_content=False"""
        with patch('engine.metrics.compute_complexity', return_value="Easy"):
            context = mock_retriever.get_file_context("utils.py", include_content=False)
            
            assert context.content == ""


class TestRelevantContextRetrieval:
    """Test relevant context retrieval for queries"""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create a mock context retriever"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "auth.py": ["models.py", "utils.py"],
                "models.py": [],
                "utils.py": [],
                "main.py": ["auth.py"],
                "router.py": ["auth.py"]
            })
            
            retriever = ContextRetriever("/fake/repo")
            return retriever
    
    def test_gets_context_with_focus_file(self, mock_retriever):
        """Should retrieve context focused on specific file"""
        with patch.object(mock_retriever, '_read_file', return_value="# content"):
            with patch('engine.metrics.compute_complexity', return_value="Medium"):
                context = mock_retriever.get_relevant_context(
                    query="What does auth.py do?",
                    focus_file="auth.py"
                )
                
                assert context["focus"] is not None
                assert context["focus"].path == "auth.py"
                assert len(context["related"]) > 0
    
    def test_gets_context_without_focus_file(self, mock_retriever):
        """Should retrieve general context when no focus file specified"""
        with patch.object(mock_retriever, '_read_file', return_value="# content"):
            with patch('engine.metrics.compute_complexity', return_value="Easy"):
                with patch('engine.metrics.rank_files_by_importance') as mock_rank:
                    mock_rank.return_value = [("models.py", 2), ("utils.py", 1)]
                    
                    context = mock_retriever.get_relevant_context(
                        query="Where should I start?"
                    )
                    
                    assert context["focus"] is None
                    assert len(context["related"]) > 0
    
    def test_limits_related_files(self, mock_retriever):
        """Should limit number of related files returned"""
        with patch.object(mock_retriever, '_read_file', return_value="# content"):
            with patch('engine.metrics.compute_complexity', return_value="Medium"):
                context = mock_retriever.get_relevant_context(
                    query="What does auth.py do?",
                    focus_file="auth.py",
                    max_files=2
                )
                
                # Should limit related files to max_files
                assert len(context["related"]) <= 2


class TestDependencyChain:
    """Test dependency chain traversal"""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create a mock context retriever with chain"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "main.py": ["auth.py"],
                "auth.py": ["models.py", "utils.py"],
                "models.py": ["database.py"],
                "utils.py": [],
                "database.py": []
            })
            
            retriever = ContextRetriever("/fake/repo")
            return retriever
    
    def test_gets_dependency_chain(self, mock_retriever):
        """Should retrieve complete dependency chain"""
        chain = mock_retriever.get_dependency_chain("main.py")
        
        assert "main.py" in chain
        assert "auth.py" in chain
        assert "models.py" in chain or "utils.py" in chain
    
    def test_limits_chain_depth(self, mock_retriever):
        """Should limit dependency chain depth"""
        chain = mock_retriever.get_dependency_chain("main.py", max_depth=1)
        
        assert "main.py" in chain
        assert "auth.py" in chain
        # Should not go deeper than max_depth
        assert len(chain) <= 2
    
    def test_handles_circular_dependencies(self, mock_retriever):
        """Should handle circular dependencies without infinite loop"""
        # Manually create circular dependency
        mock_retriever.repo_map.files["database.py"] = ["main.py"]
        
        chain = mock_retriever.get_dependency_chain("main.py", max_depth=10)
        
        # Should not hang, should return finite chain
        assert len(chain) > 0
        assert len(chain) < 20  # Reasonable upper bound


class TestImpactRadius:
    """Test impact radius calculation"""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create a mock context retriever"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "models.py": [],
                "auth.py": ["models.py"],
                "user.py": ["models.py"],
                "main.py": ["auth.py", "user.py"]
            })
            
            retriever = ContextRetriever("/fake/repo")
            return retriever
    
    def test_gets_impact_radius(self, mock_retriever):
        """Should calculate files affected by changes"""
        affected = mock_retriever.get_impact_radius("models.py")
        
        assert "models.py" in affected
        assert "auth.py" in affected
        assert "user.py" in affected
    
    def test_limits_impact_depth(self, mock_retriever):
        """Should limit impact radius depth"""
        affected = mock_retriever.get_impact_radius("models.py", max_depth=1)
        
        assert "models.py" in affected
        assert "auth.py" in affected or "user.py" in affected
        # Should not include main.py (depth 2)
        assert len(affected) <= 3


class TestRepoSummary:
    """Test repository summary generation"""
    
    def test_generates_repo_summary(self):
        """Should generate repository statistics"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "main.py": ["auth.py", "models.py"],
                "auth.py": ["models.py"],
                "models.py": [],
                "utils.py": []
            })
            
            retriever = ContextRetriever("/fake/repo")
            summary = retriever.get_repo_summary()
            
            assert summary["total_files"] == 4
            assert summary["total_dependencies"] == 3
            assert "models.py" in summary["most_imported"]
    
    def test_identifies_entry_points(self):
        """Should identify files with no importers"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "main.py": ["auth.py"],
                "auth.py": ["models.py"],
                "models.py": [],
                "standalone.py": []
            })
            
            retriever = ContextRetriever("/fake/repo")
            summary = retriever.get_repo_summary()
            
            # main.py and standalone.py have no importers
            assert "main.py" in summary["entry_points"] or "standalone.py" in summary["entry_points"]


class TestDependencyScoreIntegration:
    """Test integration with dependency score provider"""
    
    def test_uses_dependency_scores_when_enabled(self):
        """Should use dependency scores for complexity when available"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={"auth.py": []})
            
            retriever = ContextRetriever("/fake/repo", use_dependency_scores=True)
            
            assert retriever.dependency_provider is not None
    
    def test_falls_back_without_dependency_scores(self):
        """Should work without dependency score provider"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={"auth.py": []})
            
            retriever = ContextRetriever("/fake/repo", use_dependency_scores=False)
            
            assert retriever.dependency_provider is None
    
    def test_gets_files_with_scores(self):
        """Should retrieve files with dependency scores"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.return_value = RepoMap(files={
                "auth.py": [],
                "models.py": [],
                "utils.py": []
            })
            
            retriever = ContextRetriever("/fake/repo", use_dependency_scores=True)
            scored_files = retriever.get_files_with_scores(["auth.py", "models.py"])
            
            assert len(scored_files) > 0
            assert all("file_path" in f for f in scored_files)

# Made with Bob
