"""
Context Retrieval Service for IBM Bob
Intelligently fetches relevant files and relationships for each query
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from bob_core.schemas import RepoMap


@dataclass
class FileContext:
    """Context information for a single file"""
    path: str
    content: str
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    complexity: str = "Unknown"
    loc: int = 0


@dataclass
class RepoContext:
    """Complete repository context"""
    name: str
    entry_points: List[str] = field(default_factory=list)
    file_tree: Dict[str, FileContext] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)


class ContextRetriever:
    """
    Retrieves relevant context for queries
    Builds bidirectional dependency graph and caches repository structure
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize context retriever for a repository
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self.repo_map: Optional[RepoMap] = None
        self.reverse_deps: Dict[str, List[str]] = {}
        self._build_context()
    
    def _build_context(self):
        """Build complete repository context with bidirectional dependencies"""
        try:
            from engine.parser import parse_repository
            from engine.metrics import compute_complexity
            
            # Parse repository to get file tree and imports
            self.repo_map = parse_repository(self.repo_path)
            
            # Build reverse dependency map (who imports me?)
            for file_path, imports in self.repo_map.files.items():
                for imported_file in imports:
                    if imported_file not in self.reverse_deps:
                        self.reverse_deps[imported_file] = []
                    self.reverse_deps[imported_file].append(file_path)
            
        except Exception as e:
            # Fallback to empty context if parsing fails
            print(f"Warning: Failed to parse repository: {e}")
            self.repo_map = RepoMap(files={})
            self.reverse_deps = {}
    
    def get_file_context(self, file_path: str) -> Optional[FileContext]:
        """
        Get complete context for a specific file
        
        Args:
            file_path: Path to the file (relative to repo root)
        
        Returns:
            FileContext object or None if file not found
        """
        if not self.repo_map or file_path not in self.repo_map.files:
            return None
        
        try:
            from engine.metrics import compute_complexity
            
            imports = self.repo_map.files[file_path]
            imported_by = self.reverse_deps.get(file_path, [])
            complexity = compute_complexity(file_path, imports)
            content = self._read_file(file_path)
            loc = self._count_loc(content)
            
            return FileContext(
                path=file_path,
                content=content,
                imports=imports,
                imported_by=imported_by,
                complexity=complexity,
                loc=loc
            )
        except Exception as e:
            print(f"Warning: Failed to get context for {file_path}: {e}")
            return None
    
    def get_relevant_context(
        self, 
        query: str, 
        focus_file: Optional[str] = None,
        max_files: int = 5
    ) -> Dict[str, Any]:
        """
        Get relevant files based on query and optional focus file
        
        Args:
            query: User's question
            focus_file: Optional file to focus on
            max_files: Maximum number of related files to include
        
        Returns:
            Dictionary with focus file and related files
        """
        if focus_file:
            # Get file + its immediate dependencies
            context = self.get_file_context(focus_file)
            if context:
                related_files = list(set(context.imports + context.imported_by))
                related_contexts = []
                
                for f in related_files[:max_files]:
                    rel_ctx = self.get_file_context(f)
                    if rel_ctx:
                        related_contexts.append(rel_ctx)
                
                return {
                    "focus": context,
                    "related": related_contexts
                }
        
        # For general queries, return high-importance files
        try:
            from engine.metrics import rank_files_by_importance
            
            if self.repo_map and self.repo_map.files:
                ranked = rank_files_by_importance(self.repo_map.files)
                top_files = [f[0] for f in ranked[:max_files]]
                
                related_contexts = []
                for f in top_files:
                    ctx = self.get_file_context(f)
                    if ctx:
                        related_contexts.append(ctx)
                
                return {
                    "focus": None,
                    "related": related_contexts
                }
        except Exception as e:
            print(f"Warning: Failed to rank files: {e}")
        
        # Fallback: return empty context
        return {
            "focus": None,
            "related": []
        }
    
    def get_dependency_chain(self, file_path: str, max_depth: int = 3) -> List[str]:
        """
        Get dependency chain for a file (what it depends on, recursively)
        
        Args:
            file_path: Starting file
            max_depth: Maximum depth to traverse
        
        Returns:
            List of file paths in dependency order
        """
        if not self.repo_map or file_path not in self.repo_map.files:
            return []
        
        visited = set()
        chain = []
        
        def traverse(current_file: str, depth: int):
            if depth > max_depth or current_file in visited:
                return
            
            visited.add(current_file)
            chain.append(current_file)
            
            imports = self.repo_map.files.get(current_file, [])
            for imported_file in imports:
                if imported_file in self.repo_map.files:
                    traverse(imported_file, depth + 1)
        
        traverse(file_path, 0)
        return chain
    
    def get_impact_radius(self, file_path: str, max_depth: int = 3) -> List[str]:
        """
        Get impact radius for a file (what depends on it, recursively)
        
        Args:
            file_path: File to analyze
            max_depth: Maximum depth to traverse
        
        Returns:
            List of files that would be affected by changes
        """
        if not self.repo_map or file_path not in self.repo_map.files:
            return []
        
        visited = set()
        affected = []
        
        def traverse(current_file: str, depth: int):
            if depth > max_depth or current_file in visited:
                return
            
            visited.add(current_file)
            affected.append(current_file)
            
            importers = self.reverse_deps.get(current_file, [])
            for importer in importers:
                traverse(importer, depth + 1)
        
        traverse(file_path, 0)
        return affected
    
    def _read_file(self, file_path: str) -> str:
        """
        Read file content with error handling
        
        Args:
            file_path: Path relative to repo root
        
        Returns:
            File content or empty string on error
        """
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return ""
    
    def _count_loc(self, content: str) -> int:
        """
        Count lines of code (non-empty, non-comment lines)
        
        Args:
            content: File content
        
        Returns:
            Number of lines of code
        """
        if not content:
            return 0
        
        lines = content.split('\n')
        loc = 0
        
        for line in lines:
            stripped = line.strip()
            # Count non-empty lines that don't start with # (Python comments)
            if stripped and not stripped.startswith('#'):
                loc += 1
        
        return loc
    
    def get_repo_summary(self) -> Dict[str, Any]:
        """
        Get high-level repository summary
        
        Returns:
            Dictionary with repo statistics
        """
        if not self.repo_map or not self.repo_map.files:
            return {
                "total_files": 0,
                "total_dependencies": 0,
                "entry_points": [],
                "most_imported": []
            }
        
        total_files = len(self.repo_map.files)
        total_deps = sum(len(imports) for imports in self.repo_map.files.values())
        
        # Find most imported files
        import_counts = [(file, len(importers)) for file, importers in self.reverse_deps.items()]
        import_counts.sort(key=lambda x: x[1], reverse=True)
        most_imported = [f[0] for f in import_counts[:5]]
        
        # Identify potential entry points (files with no importers)
        entry_points = [
            file for file in self.repo_map.files.keys()
            if file not in self.reverse_deps or len(self.reverse_deps[file]) == 0
        ]
        
        return {
            "total_files": total_files,
            "total_dependencies": total_deps,
            "entry_points": entry_points[:5],
            "most_imported": most_imported
        }

# Made with Bob
