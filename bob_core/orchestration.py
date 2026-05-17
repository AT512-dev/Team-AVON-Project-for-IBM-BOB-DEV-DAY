"""
Compass AI Orchestration Service
Coordinates the workflow between engine layer and bob_core layer
"""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from engine.dependency_intelligence import build_dependency_intelligence
from bob_core.chunking import CodeChunker
from bob_core.context_service import ContextRetriever
from bob_core.bob_service import generate_explanation
from bob_core.schemas import DependencyIntelligencePayload, DependencyNode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompassOrchestrator:
    """
    Orchestrates the complete Compass AI workflow:
    1. Parse repository using engine/parser.py
    2. Calculate dependency intelligence using engine/dependency_intelligence.py
    3. Chunk critical files using bob_core/chunking.py
    4. Generate AI explanations using bob_core/bob_service.py
    5. Format response using bob_core/response_formatter.py
    """
    
    def __init__(self, repo_path: str, include_tests: bool = False):
        """
        Initialize orchestrator for a repository
        
        Args:
            repo_path: Path to the target repository
            include_tests: Whether to include test files in analysis
        """
        self.repo_path = repo_path
        self.include_tests = include_tests
        self.intelligence: Optional[DependencyIntelligencePayload] = None
        self.chunker = CodeChunker(max_chunk_size=500)
        
    async def analyze_repository(self) -> DependencyIntelligencePayload:
        """
        Step 1 & 2: Parse repository and calculate dependency intelligence
        
        Returns:
            Complete dependency intelligence payload
        """
        logger.info(f"Analyzing repository: {self.repo_path}")
        
        # Use Karl's dependency intelligence engine
        self.intelligence = build_dependency_intelligence(
            self.repo_path, 
            include_tests=self.include_tests
        )
        
        logger.info(f"Analysis complete: {self.intelligence.summary.total_files} files analyzed")
        return self.intelligence
    
    def get_critical_files(self, top_n: int = 10) -> List[DependencyNode]:
        """
        Get the most critical files based on dependency radius and importance
        
        Args:
            top_n: Number of top files to return
            
        Returns:
            List of critical dependency nodes
        """
        if not self.intelligence:
            raise ValueError("Must call analyze_repository() first")
        
        # Sort by importance score (highest first)
        sorted_nodes = sorted(
            self.intelligence.nodes,
            key=lambda n: (n.importance_score, n.incoming_dependency_count),
            reverse=True
        )
        
        return sorted_nodes[:top_n]
    
    async def generate_learning_roadmap(
        self, 
        max_files: int = 10,
        task_description: str = "Understand the codebase architecture"
    ) -> List[Dict[str, Any]]:
        """
        Step 3 & 4: Generate AI-powered learning roadmap
        
        Args:
            max_files: Maximum number of files to include in roadmap
            task_description: User's learning objective
            
        Returns:
            List of roadmap items with Bob's explanations
        """
        if not self.intelligence:
            await self.analyze_repository()
        
        # Type narrowing: ensure intelligence is not None
        if not self.intelligence:
            raise ValueError("Failed to analyze repository")
        
        logger.info(f"Generating learning roadmap for top {max_files} files")
        
        roadmap_items = []
        
        # Use the pre-calculated roadmap from dependency intelligence
        for roadmap_item in self.intelligence.roadmap[:max_files]:
            node = next(
                (n for n in self.intelligence.nodes if n.file == roadmap_item.file),
                None
            )
            
            if not node:
                continue
            
            # Read file content for chunking
            file_path = os.path.join(self.repo_path, roadmap_item.file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Chunk the file to avoid token limits
                chunks = self.chunker.chunk_file(content, roadmap_item.file)
                
                # Get summary of first chunk or full file if small
                context_content = chunks[0].content if chunks else content[:1000]
                
                # Generate Bob's explanation
                file_context = f"""
File: {roadmap_item.file}
Layer: {roadmap_item.architectural_layer}
Complexity Score: {roadmap_item.complexity_score}/100
Dependencies: {len(roadmap_item.prerequisites)}
Imports: {', '.join(node.dependencies[:5])}
Exported Symbols: {', '.join(node.symbols[:5])}

Code Preview:
{context_content[:500]}
"""
                
                bob_explanation = await generate_explanation(file_context, task_description)
                
            except Exception as e:
                logger.warning(f"Could not process {roadmap_item.file}: {e}")
                bob_explanation = roadmap_item.learning_reason
            
            # Determine priority based on complexity and importance
            priority = self._calculate_priority(node)
            
            roadmap_items.append({
                "step": roadmap_item.step,
                "file_path": roadmap_item.file,
                "dependencies_count": len(roadmap_item.prerequisites),
                "priority": priority,
                "bob_explanation": bob_explanation,
                "architectural_layer": roadmap_item.architectural_layer,
                "complexity_score": roadmap_item.complexity_score,
                "dependency_radius": roadmap_item.dependency_radius,
                "learning_reason": roadmap_item.learning_reason
            })
        
        logger.info(f"Generated roadmap with {len(roadmap_items)} items")
        return roadmap_items
    
    def generate_constellation_graph(self) -> Dict[str, Any]:
        """
        Step 5: Generate constellation graph for visualization
        
        Returns:
            Graph structure with nodes and edges
        """
        if not self.intelligence:
            raise ValueError("Must call analyze_repository() first")
        
        # Transform nodes for frontend
        nodes = []
        for node in self.intelligence.nodes:
            nodes.append({
                "id": node.file.replace('/', '_').replace('\\', '_').replace('.', '_'),
                "label": node.label,
                "group": node.architectural_layer.lower().replace(' ', '_'),
                "file_path": node.file,
                "complexity": node.complexity_score,
                "importance": node.importance_score,
                "incoming_deps": node.incoming_dependency_count,
                "outgoing_deps": node.outgoing_dependency_count
            })
        
        # Transform edges for frontend
        edges = []
        for edge in self.intelligence.edges:
            edges.append({
                "from": edge.source.replace('/', '_').replace('\\', '_').replace('.', '_'),
                "to": edge.target.replace('/', '_').replace('\\', '_').replace('.', '_'),
                "relationship": edge.relationship
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def calculate_dependency_radius_score(self) -> float:
        """
        Calculate overall dependency radius score for the repository
        
        Returns:
            Score from 0-10 indicating overall complexity
        """
        if not self.intelligence:
            raise ValueError("Must call analyze_repository() first")
        
        # Calculate based on multiple factors
        total_files = self.intelligence.summary.total_files
        total_edges = self.intelligence.summary.total_edges
        circular_deps = self.intelligence.summary.circular_dependency_count
        
        # Average complexity score
        avg_complexity = sum(n.complexity_score for n in self.intelligence.nodes) / total_files if total_files > 0 else 0
        
        # Average importance score
        avg_importance = sum(n.importance_score for n in self.intelligence.nodes) / total_files if total_files > 0 else 0
        
        # Normalize to 0-10 scale
        # Higher complexity, more edges, and circular deps increase the score
        base_score = (avg_complexity / 10) + (avg_importance / 10)
        edge_factor = min(total_edges / (total_files * 2), 2) if total_files > 0 else 0
        circular_penalty = min(circular_deps * 0.5, 3)
        
        final_score = min((base_score + edge_factor + circular_penalty) / 2, 10)
        
        return round(final_score, 1)
    
    def _calculate_priority(self, node: DependencyNode) -> str:
        """
        Calculate priority level for a file
        
        Args:
            node: Dependency node
            
        Returns:
            Priority level: "critical", "high", "medium", or "low"
        """
        # Critical: High importance and many dependents
        if node.importance_score >= 75 or node.incoming_dependency_count >= 5:
            return "critical"
        
        # High: Medium-high importance or foundational
        elif node.importance_score >= 50 or node.architectural_layer in ["Foundation", "Data Model"]:
            return "high"
        
        # Medium: Average importance
        elif node.importance_score >= 25:
            return "medium"
        
        # Low: Everything else
        else:
            return "low"
    
    async def generate_complete_analysis(
        self,
        max_roadmap_files: int = 10,
        task_description: str = "Understand the codebase architecture"
    ) -> Dict[str, Any]:
        """
        Generate complete Compass AI analysis
        
        This is the main orchestration method that combines all steps
        
        Args:
            max_roadmap_files: Maximum files in learning roadmap
            task_description: User's learning objective
            
        Returns:
            Complete analysis matching frontend JSON structure
        """
        logger.info("Starting complete Compass AI analysis")
        
        # Step 1 & 2: Analyze repository
        await self.analyze_repository()
        
        # Type narrowing: ensure intelligence is not None
        if not self.intelligence:
            raise ValueError("Failed to analyze repository")
        
        # Step 3 & 4: Generate learning roadmap with Bob's explanations
        learning_roadmap = await self.generate_learning_roadmap(
            max_files=max_roadmap_files,
            task_description=task_description
        )
        
        # Step 5: Generate constellation graph
        constellation_graph = self.generate_constellation_graph()
        
        # Calculate overall dependency radius score
        dependency_radius_score = self.calculate_dependency_radius_score()
        
        # Build final response
        response = {
            "status": "success",
            "dependency_radius_score": dependency_radius_score,
            "learning_roadmap": learning_roadmap,
            "constellation_graph": constellation_graph,
            "summary": {
                "total_files": self.intelligence.summary.total_files,
                "total_dependencies": self.intelligence.summary.total_edges,
                "circular_dependencies": self.intelligence.summary.circular_dependency_count,
                "architectural_layers": self.intelligence.summary.architectural_layers,
                "foundational_files": self.intelligence.summary.foundational_files,
                "hub_files": self.intelligence.summary.hub_files,
                "risky_files": self.intelligence.summary.risky_files
            }
        }
        
        logger.info("Complete analysis generated successfully")
        return response


# Convenience function for quick analysis
async def analyze_repository_for_compass(
    repo_path: str,
    max_roadmap_files: int = 10,
    task_description: str = "Understand the codebase architecture",
    include_tests: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to run complete Compass AI analysis
    
    Args:
        repo_path: Path to repository
        max_roadmap_files: Maximum files in roadmap
        task_description: Learning objective
        include_tests: Include test files
        
    Returns:
        Complete analysis result
    """
    orchestrator = CompassOrchestrator(repo_path, include_tests=include_tests)
    return await orchestrator.generate_complete_analysis(
        max_roadmap_files=max_roadmap_files,
        task_description=task_description
    )

# Made with Bob
