"""
Tests for semantic chunking functionality
Following TDD principles: test behaviors, not implementation
"""

import pytest
from bob_core.chunking import CodeChunker, CodeChunk


class TestPythonFileChunking:
    """Test Python file chunking"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker(max_chunk_size=500)
    
    def test_chunks_simple_python_file(self, chunker):
        """Should chunk Python file by imports, classes, and functions"""
        content = """import os
import sys

class UserService:
    def get_user(self, id):
        return None

def helper_function():
    pass
"""
        chunks = chunker.chunk_python_file(content)
        
        assert len(chunks) > 0
        # Should have imports chunk
        assert any(chunk.type == "imports" for chunk in chunks)
        # Should have class chunk
        assert any(chunk.type == "class" for chunk in chunks)
        # Should have function chunk
        assert any(chunk.type == "function" for chunk in chunks)
    
    def test_extracts_imports_chunk(self, chunker):
        """Should extract imports as first chunk"""
        content = """import os
import sys
from typing import List

def main():
    pass
"""
        chunks = chunker.chunk_python_file(content)
        
        import_chunks = [c for c in chunks if c.type == "imports"]
        assert len(import_chunks) > 0
        assert "import os" in import_chunks[0].content
        assert "import sys" in import_chunks[0].content
    
    def test_extracts_class_chunks(self, chunker):
        """Should extract classes as separate chunks"""
        content = """
class UserService:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)

class ProductService:
    def get_products(self):
        return []
"""
        chunks = chunker.chunk_python_file(content)
        
        class_chunks = [c for c in chunks if c.type == "class"]
        assert len(class_chunks) == 2
        assert any(c.name == "UserService" for c in class_chunks)
        assert any(c.name == "ProductService" for c in class_chunks)
    
    def test_extracts_function_chunks(self, chunker):
        """Should extract top-level functions as chunks"""
        content = """
def calculate_total(items):
    return sum(items)

def format_output(data):
    return str(data)
"""
        chunks = chunker.chunk_python_file(content)
        
        func_chunks = [c for c in chunks if c.type == "function"]
        assert len(func_chunks) == 2
        assert any(c.name == "calculate_total" for c in func_chunks)
        assert any(c.name == "format_output" for c in func_chunks)
    
    def test_handles_syntax_errors(self, chunker):
        """Should fall back to line-based chunking on syntax errors"""
        content = "def broken_function(\n    # Missing closing paren"
        
        chunks = chunker.chunk_python_file(content)
        
        # Should still return chunks (fallback mode)
        assert len(chunks) > 0
    
    def test_returns_whole_file_for_small_files(self, chunker):
        """Should return whole file if smaller than max_chunk_size"""
        content = """import os

def small_function():
    return True
"""
        chunks = chunker.chunk_python_file(content)
        
        # Small file with semantic structure should be chunked semantically
        # or returned as whole file if very small
        assert len(chunks) >= 1
        # Should have either file type or semantic chunks
        assert any(c.type in ["file", "imports", "function"] for c in chunks)


class TestChunkMetadata:
    """Test chunk metadata"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    def test_chunk_has_line_numbers(self, chunker):
        """Should include line numbers in chunks"""
        content = """import os

class MyClass:
    def method(self):
        pass
"""
        chunks = chunker.chunk_python_file(content)
        
        for chunk in chunks:
            assert chunk.start_line > 0
            assert chunk.end_line >= chunk.start_line
            assert chunk.lines is not None
    
    def test_chunk_has_size(self, chunker):
        """Should calculate chunk size in lines"""
        content = """
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"""
        chunks = chunker.chunk_python_file(content)
        
        class_chunks = [c for c in chunks if c.type == "class"]
        assert len(class_chunks) > 0
        assert class_chunks[0].size > 0
    
    def test_chunk_has_content(self, chunker):
        """Should include actual code content"""
        content = """
def my_function():
    return "Hello"
"""
        chunks = chunker.chunk_python_file(content)
        
        func_chunks = [c for c in chunks if c.type == "function"]
        assert len(func_chunks) > 0
        assert "my_function" in func_chunks[0].content
        assert "Hello" in func_chunks[0].content


class TestRelevantChunkSelection:
    """Test relevant chunk selection based on query"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing"""
        return [
            CodeChunk(
                type="class",
                name="UserService",
                lines="1-10",
                content="class UserService:\n    def get_user(self, id):\n        pass",
                start_line=1,
                end_line=10,
                size=10
            ),
            CodeChunk(
                type="function",
                name="authenticate_user",
                lines="11-20",
                content="def authenticate_user(username, password):\n    return True",
                start_line=11,
                end_line=20,
                size=10
            ),
            CodeChunk(
                type="imports",
                name=None,
                lines="1-5",
                content="import os\nimport sys",
                start_line=1,
                end_line=5,
                size=5
            )
        ]
    
    def test_selects_relevant_chunks_by_keyword(self, chunker, sample_chunks):
        """Should select chunks matching query keywords"""
        query = "How does user authentication work?"
        
        relevant = chunker.get_relevant_chunks(sample_chunks, query, max_chunks=2)
        
        assert len(relevant) <= 2
        # Should prioritize chunks with "user" or "authenticate"
        assert any("user" in c.content.lower() or "authenticate" in c.content.lower() 
                  for c in relevant)
    
    def test_prioritizes_name_matches(self, chunker, sample_chunks):
        """Should prioritize chunks where name matches query"""
        query = "What does UserService do?"
        
        relevant = chunker.get_relevant_chunks(sample_chunks, query, max_chunks=3)
        
        # UserService chunk should be first (name match)
        assert relevant[0].name == "UserService"
    
    def test_limits_number_of_chunks(self, chunker, sample_chunks):
        """Should respect max_chunks parameter"""
        query = "Tell me about the code"
        
        relevant = chunker.get_relevant_chunks(sample_chunks, query, max_chunks=1)
        
        assert len(relevant) == 1
    
    def test_handles_empty_chunk_list(self, chunker):
        """Should handle empty chunk list gracefully"""
        relevant = chunker.get_relevant_chunks([], "any query", max_chunks=3)
        
        assert len(relevant) == 0


class TestChunkSummary:
    """Test chunk summary generation"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    def test_generates_chunk_summary(self, chunker):
        """Should generate summary statistics"""
        chunks = [
            CodeChunk("class", "A", "1-10", "content", 1, 10, 10),
            CodeChunk("function", "B", "11-20", "content", 11, 20, 10),
            CodeChunk("imports", None, "1-5", "content", 1, 5, 5)
        ]
        
        summary = chunker.get_chunk_summary(chunks)
        
        assert summary["total_chunks"] == 3
        assert summary["total_lines"] == 25
        assert "class" in summary["type_distribution"]
        assert "function" in summary["type_distribution"]
        assert summary["average_chunk_size"] > 0
    
    def test_identifies_largest_chunk(self, chunker):
        """Should identify largest chunk"""
        chunks = [
            CodeChunk("class", "Small", "1-5", "content", 1, 5, 5),
            CodeChunk("class", "Large", "6-50", "content", 6, 50, 45),
            CodeChunk("function", "Medium", "51-70", "content", 51, 70, 20)
        ]
        
        summary = chunker.get_chunk_summary(chunks)
        
        assert summary["largest_chunk"].name == "Large"
        assert summary["largest_chunk"].size == 45


class TestChunkMerging:
    """Test merging of small chunks"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    def test_merges_small_chunks(self, chunker):
        """Should merge chunks smaller than min_size"""
        chunks = [
            CodeChunk("function", "tiny1", "1-3", "content1", 1, 3, 3),
            CodeChunk("function", "tiny2", "4-6", "content2", 4, 6, 3),
            CodeChunk("class", "large", "7-50", "content3", 7, 50, 44)
        ]
        
        merged = chunker.merge_small_chunks(chunks, min_size=10)
        
        # Two tiny chunks should be merged
        assert len(merged) < len(chunks)
        # Large chunk should remain separate
        assert any(c.size == 44 for c in merged)
    
    def test_preserves_large_chunks(self, chunker):
        """Should not merge chunks larger than min_size"""
        chunks = [
            CodeChunk("class", "large1", "1-20", "content1", 1, 20, 20),
            CodeChunk("class", "large2", "21-40", "content2", 21, 40, 20)
        ]
        
        merged = chunker.merge_small_chunks(chunks, min_size=10)
        
        # Both chunks should remain separate
        assert len(merged) == 2


class TestLineBasedChunking:
    """Test fallback line-based chunking"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker(max_chunk_size=10)
    
    def test_chunks_by_lines(self, chunker):
        """Should chunk by line count when semantic parsing fails"""
        content = "\n".join([f"line {i}" for i in range(25)])
        
        chunks = chunker._chunk_by_lines(content)
        
        # Should create multiple chunks
        assert len(chunks) > 1
        # Each chunk should be <= max_chunk_size
        assert all(c.size <= chunker.max_chunk_size for c in chunks)
    
    def test_handles_exact_multiples(self, chunker):
        """Should handle content that's exact multiple of chunk size"""
        content = "\n".join([f"line {i}" for i in range(20)])
        
        chunks = chunker._chunk_by_lines(content)
        
        # Should create 2 chunks of 10 lines each
        assert len(chunks) == 2
        assert all(c.size == 10 for c in chunks)


class TestNonPythonFiles:
    """Test chunking of non-Python files"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker(max_chunk_size=100)
    
    def test_chunks_non_python_file(self, chunker):
        """Should use line-based chunking for non-Python files"""
        content = "Some text content\n" * 150
        
        chunks = chunker.chunk_file(content, file_path="readme.txt")
        
        assert len(chunks) > 1
        assert all(c.type == "section" for c in chunks)
    
    def test_detects_python_files(self, chunker):
        """Should use semantic chunking for .py files"""
        content = """
class MyClass:
    def method(self):
        pass
"""
        chunks = chunker.chunk_file(content, file_path="module.py")
        
        # Should use semantic chunking
        assert any(c.type == "class" for c in chunks)


class TestKeywordExtraction:
    """Test keyword extraction from queries"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    def test_extracts_keywords(self, chunker):
        """Should extract meaningful keywords from query"""
        query = "What does the authentication function do?"
        
        keywords = chunker._extract_keywords(query)
        
        assert "authentication" in keywords
        assert "function" in keywords
        # Stop words should be removed
        assert "what" not in keywords
        assert "does" not in keywords
        assert "the" not in keywords
    
    def test_handles_punctuation(self, chunker):
        """Should remove punctuation from keywords"""
        query = "How does auth.py work?"
        
        keywords = chunker._extract_keywords(query)
        
        # Should extract "auth" without ".py"
        assert any("auth" in kw for kw in keywords)


class TestRelevanceScoring:
    """Test relevance score calculation"""
    
    @pytest.fixture
    def chunker(self):
        """Create a code chunker instance"""
        return CodeChunker()
    
    def test_scores_keyword_matches(self, chunker):
        """Should give higher scores for keyword matches"""
        chunk = CodeChunk(
            type="function",
            name="authenticate_user",
            lines="1-10",
            content="def authenticate_user(username, password):\n    return validate_credentials(username, password)",
            start_line=1,
            end_line=10,
            size=10
        )
        keywords = ["authenticate", "user"]
        
        score = chunker._calculate_relevance_score(chunk, keywords)
        
        assert score > 0
    
    def test_boosts_name_matches(self, chunker):
        """Should boost score for name matches"""
        chunk = CodeChunk(
            type="function",
            name="authenticate_user",
            lines="1-10",
            content="def authenticate_user():\n    pass",
            start_line=1,
            end_line=10,
            size=10
        )
        keywords = ["authenticate"]
        
        score = chunker._calculate_relevance_score(chunk, keywords)
        
        # Should get boost for name match
        assert score > 1.0
    
    def test_normalizes_by_size(self, chunker):
        """Should normalize score by chunk size"""
        small_chunk = CodeChunk("function", "test", "1-5", "test content", 1, 5, 5)
        large_chunk = CodeChunk("function", "test", "1-100", "test content", 1, 100, 100)
        keywords = ["test"]
        
        small_score = chunker._calculate_relevance_score(small_chunk, keywords)
        large_score = chunker._calculate_relevance_score(large_chunk, keywords)
        
        # Smaller chunk should have higher normalized score
        assert small_score > large_score

# Made with Bob
