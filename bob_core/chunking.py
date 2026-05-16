"""
Semantic Chunking Strategy
Splits large files into digestible semantic pieces for Bob's context window
"""

import ast
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Represents a semantic chunk of code"""
    type: str  # "imports", "class", "function", "other"
    name: Optional[str]  # Name of class/function, None for imports/other
    lines: str  # Line range (e.g., "1-15")
    content: str
    start_line: int
    end_line: int
    size: int  # Number of lines


class CodeChunker:
    """
    Split large files into semantic chunks
    Preserves code meaning by splitting at logical boundaries
    """
    
    MAX_CHUNK_SIZE = 500  # lines per chunk
    MIN_CHUNK_SIZE = 10   # minimum lines to consider as chunk
    
    def __init__(self, max_chunk_size: int = 500):
        """
        Initialize code chunker
        
        Args:
            max_chunk_size: Maximum lines per chunk
        """
        self.max_chunk_size = max_chunk_size
    
    def chunk_python_file(self, content: str, file_path: str = "") -> List[CodeChunk]:
        """
        Split Python file by top-level definitions
        
        Args:
            content: File content as string
            file_path: Optional file path for context
        
        Returns:
            List of CodeChunk objects
        """
        try:
            tree = ast.parse(content)
            chunks = []
            lines = content.split('\n')
            
            # Extract imports first
            import_nodes = [
                node for node in tree.body 
                if isinstance(node, (ast.Import, ast.ImportFrom))
            ]
            
            if import_nodes:
                last_import = import_nodes[-1]
                import_content = '\n'.join(lines[:last_import.lineno])
                chunks.append(CodeChunk(
                    type="imports",
                    name=None,
                    lines=f"1-{last_import.lineno}",
                    content=import_content,
                    start_line=1,
                    end_line=last_import.lineno,
                    size=last_import.lineno
                ))
            
            # Extract classes and functions
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    chunk = self._extract_class_chunk(node, lines)
                    if chunk:
                        chunks.append(chunk)
                
                elif isinstance(node, ast.FunctionDef):
                    chunk = self._extract_function_chunk(node, lines)
                    if chunk:
                        chunks.append(chunk)
            
            # If no chunks were created or file is small, return whole file
            if not chunks or len(lines) <= self.max_chunk_size:
                return [CodeChunk(
                    type="file",
                    name=file_path,
                    lines=f"1-{len(lines)}",
                    content=content,
                    start_line=1,
                    end_line=len(lines),
                    size=len(lines)
                )]
            
            return chunks
            
        except SyntaxError:
            # If parsing fails, fall back to line-based chunking
            return self._chunk_by_lines(content, file_path)
    
    def chunk_file(self, content: str, file_path: str = "") -> List[CodeChunk]:
        """
        Chunk any file (attempts Python parsing, falls back to line-based)
        
        Args:
            content: File content
            file_path: File path for context
        
        Returns:
            List of CodeChunk objects
        """
        if file_path.endswith('.py'):
            return self.chunk_python_file(content, file_path)
        else:
            return self._chunk_by_lines(content, file_path)
    
    def get_relevant_chunks(
        self, 
        chunks: List[CodeChunk], 
        query: str,
        max_chunks: int = 3
    ) -> List[CodeChunk]:
        """
        Select most relevant chunks based on query
        
        Args:
            chunks: List of code chunks
            query: User's question
            max_chunks: Maximum number of chunks to return
        
        Returns:
            List of most relevant chunks
        """
        # Simple keyword matching for now
        # TODO: Use embeddings for semantic similarity
        keywords = self._extract_keywords(query)
        scored_chunks = []
        
        for chunk in chunks:
            score = self._calculate_relevance_score(chunk, keywords)
            scored_chunks.append((score, chunk))
        
        # Sort by score (highest first)
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        # Return top chunks
        return [chunk for score, chunk in scored_chunks[:max_chunks]]
    
    def get_chunk_summary(self, chunks: List[CodeChunk]) -> Dict[str, Any]:
        """
        Get summary statistics about chunks
        
        Args:
            chunks: List of code chunks
        
        Returns:
            Dictionary with summary statistics
        """
        total_lines = sum(chunk.size for chunk in chunks)
        
        type_counts = {}
        for chunk in chunks:
            type_counts[chunk.type] = type_counts.get(chunk.type, 0) + 1
        
        return {
            "total_chunks": len(chunks),
            "total_lines": total_lines,
            "type_distribution": type_counts,
            "average_chunk_size": total_lines / len(chunks) if chunks else 0,
            "largest_chunk": max(chunks, key=lambda c: c.size) if chunks else None
        }
    
    def merge_small_chunks(
        self, 
        chunks: List[CodeChunk], 
        min_size: int = 10
    ) -> List[CodeChunk]:
        """
        Merge chunks that are too small
        
        Args:
            chunks: List of code chunks
            min_size: Minimum chunk size in lines
        
        Returns:
            List of merged chunks
        """
        if not chunks:
            return []
        
        merged = []
        current_merge = None
        
        for chunk in chunks:
            if chunk.size < min_size:
                if current_merge is None:
                    current_merge = chunk
                else:
                    # Merge with previous small chunk
                    current_merge = self._merge_two_chunks(current_merge, chunk)
            else:
                if current_merge:
                    merged.append(current_merge)
                    current_merge = None
                merged.append(chunk)
        
        # Add any remaining merged chunk
        if current_merge:
            merged.append(current_merge)
        
        return merged
    
    def _extract_class_chunk(self, node: ast.ClassDef, lines: List[str]) -> Optional[CodeChunk]:
        """Extract a class definition as a chunk"""
        if not hasattr(node, 'end_lineno') or node.end_lineno is None:
            return None
        
        start = node.lineno - 1  # 0-indexed
        end = node.end_lineno
        
        content = '\n'.join(lines[start:end])
        
        return CodeChunk(
            type="class",
            name=node.name,
            lines=f"{node.lineno}-{node.end_lineno}",
            content=content,
            start_line=node.lineno,
            end_line=node.end_lineno,
            size=node.end_lineno - node.lineno + 1
        )
    
    def _extract_function_chunk(self, node: ast.FunctionDef, lines: List[str]) -> Optional[CodeChunk]:
        """Extract a function definition as a chunk"""
        if not hasattr(node, 'end_lineno') or node.end_lineno is None:
            return None
        
        start = node.lineno - 1  # 0-indexed
        end = node.end_lineno
        
        content = '\n'.join(lines[start:end])
        
        return CodeChunk(
            type="function",
            name=node.name,
            lines=f"{node.lineno}-{node.end_lineno}",
            content=content,
            start_line=node.lineno,
            end_line=node.end_lineno,
            size=node.end_lineno - node.lineno + 1
        )
    
    def _chunk_by_lines(self, content: str, file_path: str = "") -> List[CodeChunk]:
        """
        Fallback: split by line count
        
        Args:
            content: File content
            file_path: File path for context
        
        Returns:
            List of line-based chunks
        """
        lines = content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), self.max_chunk_size):
            end = min(i + self.max_chunk_size, len(lines))
            chunk_lines = lines[i:end]
            chunk_content = '\n'.join(chunk_lines)
            
            chunks.append(CodeChunk(
                type="section",
                name=f"Lines {i+1}-{end}",
                lines=f"{i+1}-{end}",
                content=chunk_content,
                start_line=i + 1,
                end_line=end,
                size=len(chunk_lines)
            ))
        
        return chunks
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query
        
        Args:
            query: User's question
        
        Returns:
            List of keywords
        """
        # Remove common words
        stop_words = {
            'what', 'does', 'how', 'why', 'when', 'where', 'who',
            'is', 'are', 'the', 'a', 'an', 'this', 'that', 'these', 'those',
            'do', 'does', 'did', 'can', 'could', 'should', 'would'
        }
        
        words = query.lower().split()
        keywords = [w.strip('?.,!') for w in words if w.lower() not in stop_words]
        
        return keywords
    
    def _calculate_relevance_score(self, chunk: CodeChunk, keywords: List[str]) -> float:
        """
        Calculate relevance score for a chunk
        
        Args:
            chunk: Code chunk
            keywords: List of keywords from query
        
        Returns:
            Relevance score (higher is more relevant)
        """
        score = 0.0
        content_lower = chunk.content.lower()
        
        # Check for keyword matches in content
        for keyword in keywords:
            if keyword in content_lower:
                score += 1.0
        
        # Boost score if keyword matches chunk name
        if chunk.name:
            name_lower = chunk.name.lower()
            for keyword in keywords:
                if keyword in name_lower:
                    score += 2.0
        
        # Boost imports chunk for "import" related queries
        if chunk.type == "imports" and any(k in ["import", "dependency", "dependencies"] for k in keywords):
            score += 3.0
        
        # Normalize by chunk size (prefer smaller, focused chunks)
        if chunk.size > 0:
            score = score / (1 + chunk.size / 100.0)
        
        return score
    
    def _merge_two_chunks(self, chunk1: CodeChunk, chunk2: CodeChunk) -> CodeChunk:
        """
        Merge two chunks into one
        
        Args:
            chunk1: First chunk
            chunk2: Second chunk
        
        Returns:
            Merged chunk
        """
        merged_content = chunk1.content + '\n' + chunk2.content
        
        return CodeChunk(
            type="merged",
            name=f"{chunk1.name or 'section'} + {chunk2.name or 'section'}",
            lines=f"{chunk1.start_line}-{chunk2.end_line}",
            content=merged_content,
            start_line=chunk1.start_line,
            end_line=chunk2.end_line,
            size=chunk1.size + chunk2.size
        )

# Made with Bob
