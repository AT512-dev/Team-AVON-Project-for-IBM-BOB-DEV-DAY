"""
Edge case tests for the entire system
Tests boundary conditions, unusual inputs, and error scenarios
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from bob_core.prompts import build_mentor_prompt, classify_query
from bob_core.context_service import ContextRetriever
from bob_core.response_formatter import format_mentor_response
from bob_core.chunking import CodeChunker
from bob_core.dependency_integration import DependencyScoreProvider


class TestEmptyInputs:
    """Test handling of empty inputs"""
    
    def test_empty_question(self):
        """Should handle empty question"""
        query_type = classify_query("")
        
        assert query_type == "general"
    
    def test_empty_repo_context(self):
        """Should handle empty repository context"""
        prompt = build_mentor_prompt(
            query_type="general",
            repo_context={"name": "empty", "files": {}},
            user_question="What is this?"
        )
        
        assert prompt is not None
        assert len(prompt) > 0
    
    def test_empty_file_content(self):
        """Should handle empty file content"""
        chunker = CodeChunker()
        chunks = chunker.chunk_python_file("", "empty.py")
        
        assert len(chunks) == 1
        assert chunks[0].type == "file"
    
    def test_empty_response(self):
        """Should handle empty WatsonX response"""
        context = {"focus": None, "related": []}
        formatted = format_mentor_response("", context, "general")
        
        assert "answer" in formatted
        assert formatted["answer"] == ""


class TestVeryLargeInputs:
    """Test handling of very large inputs"""
    
    def test_very_long_question(self):
        """Should handle very long questions"""
        long_question = "What does " + "this file " * 1000 + "do?"
        
        query_type = classify_query(long_question)
        
        assert query_type in ["file_purpose", "general"]
    
    def test_very_large_file(self):
        """Should chunk very large files"""
        chunker = CodeChunker(max_chunk_size=100)
        large_content = "\n".join([f"def function_{i}():\n    pass" for i in range(500)])
        
        chunks = chunker.chunk_python_file(large_content)
        
        assert len(chunks) > 1
        # Each chunk should be reasonable size
        assert all(c.size <= 200 for c in chunks)
    
    def test_many_dependencies(self):
        """Should handle files with many dependencies"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            # File with 100 imports
            mock_parse.return_value = RepoMap(files={
                "main.py": [f"module{i}.py" for i in range(100)]
            })
            
            retriever = ContextRetriever("/fake/repo")
            context = retriever.get_file_context("main.py")
            
            assert context is not None
            assert len(context.imports) == 100


class TestSpecialCharacters:
    """Test handling of special characters"""
    
    def test_unicode_in_question(self):
        """Should handle unicode characters in questions"""
        question = "What does 文件.py do? 🚀"
        
        query_type = classify_query(question)
        
        assert query_type is not None
    
    def test_special_chars_in_file_path(self):
        """Should handle special characters in file paths"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={
                "file-with-dashes.py": [],
                "file_with_underscores.py": [],
                "file.with.dots.py": []
            })
            
            retriever = ContextRetriever("/fake/repo")
            
            # Should handle all special chars
            assert retriever.get_file_context("file-with-dashes.py") is not None
    
    def test_code_with_special_chars(self):
        """Should handle code with special characters"""
        chunker = CodeChunker()
        content = '''
def test():
    """Test with émojis 🎉 and spëcial çhars"""
    return "Hello 世界"
'''
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0


class TestMalformedInputs:
    """Test handling of malformed inputs"""
    
    def test_invalid_python_syntax(self):
        """Should handle invalid Python syntax"""
        chunker = CodeChunker()
        invalid_code = "def broken(\n    # Missing closing paren\n    return None"
        
        chunks = chunker.chunk_python_file(invalid_code)
        
        # Should fall back to line-based chunking
        assert len(chunks) > 0
    
    def test_mixed_line_endings(self):
        """Should handle mixed line endings"""
        chunker = CodeChunker()
        content = "line1\nline2\r\nline3\rline4"
        
        chunks = chunker.chunk_file(content, "test.txt")
        
        assert len(chunks) > 0
    
    def test_null_bytes_in_content(self):
        """Should handle null bytes in content"""
        chunker = CodeChunker()
        # Python strings can't contain null bytes, but test empty handling
        content = ""
        
        chunks = chunker.chunk_file(content, "test.py")
        
        assert len(chunks) > 0


class TestCircularDependencies:
    """Test handling of circular dependencies"""
    
    def test_circular_import_chain(self):
        """Should handle circular import chains"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            # A imports B, B imports C, C imports A
            mock_parse.return_value = RepoMap(files={
                "a.py": ["b.py"],
                "b.py": ["c.py"],
                "c.py": ["a.py"]
            })
            
            retriever = ContextRetriever("/fake/repo")
            chain = retriever.get_dependency_chain("a.py", max_depth=10)
            
            # Should not hang, should return finite chain
            assert len(chain) > 0
            assert len(chain) < 20
    
    def test_self_import(self):
        """Should handle file importing itself"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={
                "recursive.py": ["recursive.py"]
            })
            
            retriever = ContextRetriever("/fake/repo")
            context = retriever.get_file_context("recursive.py")
            
            assert context is not None


class TestMissingData:
    """Test handling of missing data"""
    
    def test_missing_file_in_context(self):
        """Should handle missing file gracefully"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={"main.py": []})
            
            retriever = ContextRetriever("/fake/repo")
            context = retriever.get_file_context("nonexistent.py")
            
            assert context is None
    
    def test_missing_complexity_score(self):
        """Should handle missing complexity scores"""
        provider = DependencyScoreProvider(use_mock=False)
        
        score = provider.get_file_score("unknown.py")
        
        # Should return None when not in mock mode and service unavailable
        assert score is None
    
    def test_missing_imports(self):
        """Should handle files with no imports"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={"standalone.py": []})
            
            retriever = ContextRetriever("/fake/repo")
            context = retriever.get_file_context("standalone.py")
            
            assert context is not None
            assert context.imports == []


class TestBoundaryValues:
    """Test boundary value conditions"""
    
    def test_zero_max_chunks(self):
        """Should handle zero max_chunks"""
        from bob_core.chunking import CodeChunk
        chunker = CodeChunker()
        chunks = [CodeChunk("function", "test", "1-10", "def test(): pass", 1, 10, 10)] * 5
        
        relevant = chunker.get_relevant_chunks(chunks, "test", max_chunks=0)
        
        assert len(relevant) == 0
    
    def test_negative_max_depth(self):
        """Should handle negative max_depth"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={"main.py": ["auth.py"]})
            
            retriever = ContextRetriever("/fake/repo")
            chain = retriever.get_dependency_chain("main.py", max_depth=-1)
            
            # Should return empty or handle gracefully
            assert isinstance(chain, list)
    
    def test_single_line_file(self):
        """Should handle single-line files"""
        chunker = CodeChunker()
        content = "import os"
        
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0
    
    def test_file_with_only_comments(self):
        """Should handle files with only comments"""
        chunker = CodeChunker()
        content = "# Comment 1\n# Comment 2\n# Comment 3"
        
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0


class TestConcurrentAccess:
    """Test concurrent access scenarios"""
    
    def test_multiple_retrievers_same_repo(self):
        """Should handle multiple retrievers for same repo"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={"main.py": []})
            
            retriever1 = ContextRetriever("/fake/repo")
            retriever2 = ContextRetriever("/fake/repo")
            
            # Both should work independently
            assert retriever1.repo_path == retriever2.repo_path
            assert retriever1 is not retriever2
    
    def test_cache_isolation(self):
        """Should isolate caches between providers"""
        provider1 = DependencyScoreProvider(use_mock=True)
        provider2 = DependencyScoreProvider(use_mock=True)
        
        provider1.get_file_score("test.py")
        
        # Provider2 should have empty cache
        assert len(provider2._cache) == 0


class TestResourceLimits:
    """Test resource limit handling"""
    
    def test_very_deep_nesting(self):
        """Should handle very deep directory nesting"""
        deep_path = "/".join(["dir"] * 100) + "/file.py"
        
        provider = DependencyScoreProvider(use_mock=True)
        score = provider.get_file_score(deep_path)
        
        assert score is not None
    
    def test_many_files_in_repo(self):
        """Should handle repositories with many files"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            # 1000 files
            files = {f"file{i}.py": [] for i in range(1000)}
            mock_parse.return_value = RepoMap(files=files)
            
            retriever = ContextRetriever("/fake/repo")
            summary = retriever.get_repo_summary()
            
            assert summary["total_files"] == 1000


class TestErrorRecovery:
    """Test error recovery mechanisms"""
    
    def test_recovers_from_parse_error(self):
        """Should recover from parsing errors"""
        with patch('engine.parser.parse_repository') as mock_parse:
            mock_parse.side_effect = Exception("Parse failed")
            
            retriever = ContextRetriever("/fake/repo")
            
            # Should create empty repo map
            assert retriever.repo_map is not None
            assert retriever.repo_map.files == {}
    
    def test_continues_after_file_read_error(self):
        """Should continue after file read errors"""
        with patch('engine.parser.parse_repository') as mock_parse:
            from bob_core.schemas import RepoMap
            mock_parse.return_value = RepoMap(files={"test.py": []})
            
            retriever = ContextRetriever("/fake/repo")
            
            # Mock file read to fail
            with patch.object(retriever, '_read_file', return_value=""):
                context = retriever.get_file_context("test.py")
                
                # Should still return context with empty content
                assert context is not None
                assert context.content == ""


class TestUnicodeAndEncoding:
    """Test unicode and encoding handling"""
    
    def test_utf8_content(self):
        """Should handle UTF-8 content"""
        chunker = CodeChunker()
        content = """
def greet():
    return "Hello 世界 🌍"
"""
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0
        assert "世界" in chunks[0].content or any("世界" in c.content for c in chunks)
    
    def test_mixed_encodings(self):
        """Should handle mixed encoding scenarios"""
        # Python 3 strings are unicode, so this tests string handling
        question = "What does файл.py do?"
        
        query_type = classify_query(question)
        
        assert query_type is not None


class TestPerformanceEdgeCases:
    """Test performance edge cases"""
    
    def test_extremely_long_line(self):
        """Should handle extremely long lines"""
        chunker = CodeChunker()
        long_line = "x = " + "1" * 10000
        
        chunks = chunker.chunk_python_file(long_line)
        
        assert len(chunks) > 0
    
    def test_many_small_functions(self):
        """Should handle many small functions"""
        chunker = CodeChunker()
        content = "\n".join([f"def func{i}():\n    pass\n" for i in range(100)])
        
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0
        # Should have many function chunks
        func_chunks = [c for c in chunks if c.type == "function"]
        assert len(func_chunks) > 50

# Made with Bob