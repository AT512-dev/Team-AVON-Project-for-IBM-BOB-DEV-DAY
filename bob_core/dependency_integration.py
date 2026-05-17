"""
Dependency Integration Service
Integrates engine layer (parser, metrics, dependency_intelligence) with bob_core layer
Provides a unified interface for accessing dependency analysis results
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from engine.dependency_intelligence import build_dependency_intelligence, DependencyIntelligencePayload
from bob_core.schemas import DependencyNode


@dataclass
class DependencyScore:
    """Dependency score information from engine layer"""
    file_path: str
    complexity: float  # 0-1 scale (normalized from 0-100)
    centrality: float  # 0-1 scale (based on incoming dependencies)
    distance_from_entry: int  # dependency radius
    recommendation: str  # "start_here" | "study_later" | "advanced"
    importance_score: int  # 0-100 scale
    architectural_layer: str


class DependencyScoreProvider:
    """
    Interface to engine layer dependency intelligence
    Provides complexity and centrality scores for files using real analysis
    """
    
    def __init__(self, repo_path: Optional[str] = None, use_mock: bool = False):
        """
        Initialize dependency score provider
        
        Args:
            repo_path: Path to repository for real analysis
            use_mock: If True, use mock data. If False, use engine layer analysis.
        """
        self.use_mock = use_mock
        self.repo_path = repo_path
        self._cache: Dict[str, DependencyScore] = {}
        self._intelligence: Optional[DependencyIntelligencePayload] = None
        
        # Load real intelligence if repo_path provided and not using mock
        if repo_path and not use_mock:
            self._load_intelligence()
    
    def _load_intelligence(self):
        """Load dependency intelligence from engine layer"""
        if not self.repo_path:
            return
        
        try:
            self._intelligence = build_dependency_intelligence(self.repo_path, include_tests=False)
            
            # Pre-populate cache with real data
            for node in self._intelligence.nodes:
                score = self._node_to_score(node)
                self._cache[node.file] = score
                
        except Exception as e:
            print(f"Warning: Failed to load dependency intelligence: {e}")
            self._intelligence = None
    
    def _node_to_score(self, node: DependencyNode) -> DependencyScore:
        """Convert DependencyNode to DependencyScore"""
        # Normalize complexity to 0-1 scale
        complexity = node.complexity_score / 100.0
        
        # Calculate centrality based on incoming dependencies
        # Normalize to 0-1 scale (assume max 20 incoming deps)
        centrality = min(node.incoming_dependency_count / 20.0, 1.0)
        
        # Determine recommendation based on scores
        if complexity < 0.33 and node.architectural_layer in ["Foundation", "Configuration", "Data Model"]:
            recommendation = "start_here"
        elif complexity < 0.67:
            recommendation = "study_later"
        else:
            recommendation = "advanced"
        
        return DependencyScore(
            file_path=node.file,
            complexity=complexity,
            centrality=centrality,
            distance_from_entry=node.dependency_radius,
            recommendation=recommendation,
            importance_score=node.importance_score,
            architectural_layer=node.architectural_layer
        )
    
    def get_file_score(self, file_path: str) -> Optional[DependencyScore]:
        """
        Get Karl's dependency radius score for a file
        
        Args:
            file_path: Path to the file
        
        Returns:
            DependencyScore object or None if not available
        """
        # Check cache first
        if file_path in self._cache:
            return self._cache[file_path]
        
        if self.use_mock:
            score = self._get_mock_score(file_path)
        else:
            # Use real intelligence from engine layer
            if self._intelligence:
                node = next((n for n in self._intelligence.nodes if n.file == file_path), None)
                if node:
                    score = self._node_to_score(node)
                else:
                    score = None
            else:
                score = None
        
        # Cache the result
        if score:
            self._cache[file_path] = score
        
        return score
    
    def get_learning_path(self, files: List[str], task: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recommended file order based on dependency scores
        
        Args:
            files: List of file paths
            task: Optional task description to influence ordering
        
        Returns:
            List of files with scores, sorted by learning order
        """
        scored_files = []
        
        for file_path in files:
            score = self.get_file_score(file_path)
            if score:
                # Calculate learning priority
                # Lower complexity + higher centrality = study first
                priority = self._calculate_priority(score)
                
                scored_files.append({
                    "file_path": file_path,
                    "complexity": self._complexity_label(score.complexity),
                    "centrality": score.centrality,
                    "distance_from_entry": score.distance_from_entry,
                    "recommendation": score.recommendation,
                    "priority": priority
                })
        
        # Sort by priority (lower = study first)
        scored_files.sort(key=lambda x: x["priority"])
        
        return scored_files
    
    def get_complexity_distribution(self, files: List[str]) -> Dict[str, int]:
        """
        Get distribution of complexity levels across files
        
        Args:
            files: List of file paths
        
        Returns:
            Dictionary with counts for each complexity level
        """
        distribution = {"Easy": 0, "Medium": 0, "Hard": 0}
        
        for file_path in files:
            score = self.get_file_score(file_path)
            if score:
                label = self._complexity_label(score.complexity)
                distribution[label] += 1
        
        return distribution
    
    def get_entry_points(self, files: List[str]) -> List[str]:
        """
        Identify entry point files (distance_from_entry = 0)
        
        Args:
            files: List of file paths
        
        Returns:
            List of entry point file paths
        """
        entry_points = []
        
        for file_path in files:
            score = self.get_file_score(file_path)
            if score and score.distance_from_entry == 0:
                entry_points.append(file_path)
        
        return entry_points
    
    def get_central_files(self, files: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get most central files (highest centrality scores)
        
        Args:
            files: List of file paths
            top_n: Number of top files to return
        
        Returns:
            List of most central files with scores
        """
        scored_files = []
        
        for file_path in files:
            score = self.get_file_score(file_path)
            if score:
                scored_files.append({
                    "file_path": file_path,
                    "centrality": score.centrality,
                    "complexity": self._complexity_label(score.complexity)
                })
        
        # Sort by centrality (highest first)
        scored_files.sort(key=lambda x: x["centrality"], reverse=True)
        
        return scored_files[:top_n]
    
    def _calculate_priority(self, score: DependencyScore) -> float:
        """
        Calculate learning priority score
        Lower score = study first
        
        Args:
            score: DependencyScore object
        
        Returns:
            Priority score (0-10, lower is higher priority)
        """
        # Factors:
        # - Lower complexity = higher priority
        # - Higher centrality = higher priority
        # - Closer to entry = higher priority
        
        complexity_weight = score.complexity * 3  # 0-3
        centrality_weight = (1 - score.centrality) * 3  # 0-3 (inverted)
        distance_weight = min(score.distance_from_entry * 0.5, 4)  # 0-4
        
        priority = complexity_weight + centrality_weight + distance_weight
        
        return priority
    
    def _complexity_label(self, complexity: float) -> str:
        """
        Convert complexity score to label
        
        Args:
            complexity: Complexity score (0-1)
        
        Returns:
            "Easy", "Medium", or "Hard"
        """
        if complexity < 0.33:
            return "Easy"
        elif complexity < 0.67:
            return "Medium"
        else:
            return "Hard"
    
    def _get_mock_score(self, file_path: str) -> DependencyScore:
        """
        Generate mock dependency score for testing
        
        Args:
            file_path: Path to the file
        
        Returns:
            Mock DependencyScore object
        """
        # Generate deterministic mock scores based on file name
        file_hash = hash(file_path) % 100
        
        # Determine complexity based on file name patterns
        if "utils" in file_path.lower() or "helper" in file_path.lower():
            complexity = 0.2  # Easy
            recommendation = "start_here"
        elif "main" in file_path.lower() or "app" in file_path.lower():
            complexity = 0.5  # Medium
            recommendation = "study_later"
        elif "service" in file_path.lower() or "controller" in file_path.lower():
            complexity = 0.7  # Hard
            recommendation = "advanced"
        else:
            complexity = (file_hash % 100) / 100.0
            if complexity < 0.33:
                recommendation = "start_here"
            elif complexity < 0.67:
                recommendation = "study_later"
            else:
                recommendation = "advanced"
        
        # Centrality: files with common names tend to be more central
        if any(name in file_path.lower() for name in ["models", "utils", "config", "database"]):
            centrality = 0.7 + (file_hash % 30) / 100.0
        else:
            centrality = (file_hash % 70) / 100.0
        
        # Distance from entry: estimate based on file location
        if "main" in file_path.lower() or "app" in file_path.lower():
            distance = 0
        elif "/" in file_path or "\\" in file_path:
            distance = file_path.count("/") + file_path.count("\\")
        else:
            distance = 1
        
        return DependencyScore(
            file_path=file_path,
            complexity=complexity,
            centrality=centrality,
            distance_from_entry=distance,
            recommendation=recommendation,
            importance_score=int(centrality * 100),
            architectural_layer="Application Logic"
        )
    
    def get_intelligence_payload(self) -> Optional[DependencyIntelligencePayload]:
        """
        Get the complete dependency intelligence payload
        
        Returns:
            DependencyIntelligencePayload or None if not loaded
        """
        return self._intelligence
    
    def reload_intelligence(self, repo_path: Optional[str] = None):
        """
        Reload dependency intelligence from engine layer
        
        Args:
            repo_path: Optional new repository path
        """
        if repo_path:
            self.repo_path = repo_path
        
        self._cache.clear()
        self._intelligence = None
        
        if self.repo_path and not self.use_mock:
            self._load_intelligence()
    
    def clear_cache(self):
        """Clear the score cache"""
        self._cache.clear()
    
    def preload_scores(self, files: List[str]):
        """
        Preload scores for multiple files (batch operation)
        
        Args:
            files: List of file paths to preload
        """
        for file_path in files:
            self.get_file_score(file_path)

# Made with Bob
