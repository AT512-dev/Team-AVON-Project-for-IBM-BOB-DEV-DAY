"""
Response Formatter for IBM Bob
Structures raw WatsonX responses into JSON format for UI consumption
"""

import re
from typing import Dict, List, Any, Optional
from bob_core.context_service import FileContext


def format_mentor_response(
    raw_response: str,
    context: Dict[str, Any],
    query_type: str
) -> Dict[str, Any]:
    """
    Format Bob's raw text response into structured JSON
    
    Args:
        raw_response: Raw text from WatsonX API
        context: Context used for the query (focus file + related files)
        query_type: Type of query (file_purpose, where_to_start, etc.)
    
    Returns:
        Structured response with answer, cited files, and next steps
    """
    # Extract cited files from response (files mentioned in backticks)
    cited_files = extract_cited_files(raw_response, context)
    
    # Extract next steps or recommendations
    next_steps = extract_next_steps(raw_response)
    
    # Get related files from context
    related_files = get_related_files(context)
    
    # Calculate confidence based on context availability
    confidence = calculate_confidence(context, cited_files)
    
    return {
        "answer": raw_response.strip(),
        "cited_files": cited_files,
        "related_files": related_files,
        "next_steps": next_steps,
        "confidence": confidence,
        "query_type": query_type
    }


def extract_cited_files(raw_response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract files cited in the response (mentioned in backticks)
    
    Args:
        raw_response: Raw text response
        context: Query context with file information
    
    Returns:
        List of cited files with metadata
    """
    # Find all files mentioned in backticks (e.g., `auth.py`)
    pattern = r'`([^`]+\.py)`'
    mentioned_files = re.findall(pattern, raw_response)
    
    cited = []
    seen = set()
    
    # Add focus file first if it exists
    focus = context.get("focus")
    if focus and isinstance(focus, FileContext):
        cited.append({
            "path": focus.path,
            "reason": "Primary file in question",
            "complexity": focus.complexity,
            "loc": focus.loc
        })
        seen.add(focus.path)
    
    # Add mentioned files
    for file_path in mentioned_files:
        if file_path not in seen:
            # Try to find this file in context
            file_info = find_file_in_context(file_path, context)
            if file_info:
                cited.append(file_info)
                seen.add(file_path)
    
    # Add related files from context if not already cited
    related = context.get("related", [])
    for file_ctx in related[:3]:  # Limit to top 3 related files
        if isinstance(file_ctx, FileContext) and file_ctx.path not in seen:
            cited.append({
                "path": file_ctx.path,
                "reason": "Related dependency",
                "complexity": file_ctx.complexity,
                "loc": file_ctx.loc
            })
            seen.add(file_ctx.path)
    
    return cited


def find_file_in_context(file_path: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Find file information in the context
    
    Args:
        file_path: File path to find
        context: Query context
    
    Returns:
        File information dict or None
    """
    # Check focus file
    focus = context.get("focus")
    if focus and isinstance(focus, FileContext) and focus.path == file_path:
        return {
            "path": focus.path,
            "reason": "Mentioned in response",
            "complexity": focus.complexity,
            "loc": focus.loc
        }
    
    # Check related files
    related = context.get("related", [])
    for file_ctx in related:
        if isinstance(file_ctx, FileContext) and file_ctx.path == file_path:
            return {
                "path": file_ctx.path,
                "reason": "Mentioned in response",
                "complexity": file_ctx.complexity,
                "loc": file_ctx.loc
            }
    
    # File not in context, return basic info
    return {
        "path": file_path,
        "reason": "Mentioned in response",
        "complexity": "Unknown",
        "loc": 0
    }


def extract_next_steps(raw_response: str) -> List[str]:
    """
    Extract actionable next steps from response
    
    Args:
        raw_response: Raw text response
    
    Returns:
        List of next step recommendations
    """
    next_steps = []
    
    # Look for common patterns indicating next steps
    patterns = [
        r'(?:start by|begin with|first,?\s+(?:study|check|review|understand))\s+([^.!?]+)',
        r'(?:next,?\s+(?:study|check|review|look at))\s+([^.!?]+)',
        r'(?:then,?\s+(?:study|check|review|examine))\s+([^.!?]+)',
        r'(?:you should|recommend|suggest)\s+(?:studying|checking|reviewing)\s+([^.!?]+)',
        r'(?:start\s+(?:by\s+)?studying|check)\s+([a-zA-Z_]+\.py)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, raw_response, re.IGNORECASE)
        for match in matches:
            step = match.strip()
            if step and len(step) < 150:  # Reasonable length
                next_steps.append(step)
    
    # If no explicit steps found, extract sentences with file mentions
    if not next_steps:
        sentences = raw_response.split('.')
        for sentence in sentences:
            if '`' in sentence and any(word in sentence.lower() for word in ['study', 'check', 'review', 'understand', 'look']):
                step = sentence.strip()
                if step and len(step) < 150:
                    next_steps.append(step)
    
    # Deduplicate and limit
    seen = set()
    unique_steps = []
    for step in next_steps:
        step_lower = step.lower()
        if step_lower not in seen:
            seen.add(step_lower)
            unique_steps.append(step)
    
    return unique_steps[:5]  # Limit to 5 steps


def get_related_files(context: Dict[str, Any]) -> List[str]:
    """
    Get list of related file paths from context
    
    Args:
        context: Query context
    
    Returns:
        List of related file paths
    """
    related_paths = []
    
    # Get from focus file's dependencies
    focus = context.get("focus")
    if focus and isinstance(focus, FileContext):
        related_paths.extend(focus.imports)
        related_paths.extend(focus.imported_by)
    
    # Get from related files
    related = context.get("related", [])
    for file_ctx in related:
        if isinstance(file_ctx, FileContext):
            if file_ctx.path not in related_paths:
                related_paths.append(file_ctx.path)
    
    # Deduplicate and limit
    seen = set()
    unique_paths = []
    for path in related_paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)
    
    return unique_paths[:10]  # Limit to 10 related files


def calculate_confidence(context: Dict[str, Any], cited_files: List[Dict[str, Any]]) -> float:
    """
    Calculate confidence score based on context availability
    
    Args:
        context: Query context
        cited_files: Files cited in response
    
    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence
    
    # Increase confidence if we have focus file
    if context.get("focus"):
        confidence += 0.2
    
    # Increase confidence based on number of related files
    related = context.get("related", [])
    if len(related) > 0:
        confidence += min(0.15, len(related) * 0.05)
    
    # Increase confidence based on cited files
    if len(cited_files) > 0:
        confidence += min(0.15, len(cited_files) * 0.03)
    
    # Cap at 0.95 (never 100% certain)
    return min(0.95, confidence)


def format_error_response(error_message: str, query_type: str = "general") -> Dict[str, Any]:
    """
    Format error response when something goes wrong
    
    Args:
        error_message: Error description
        query_type: Type of query that failed
    
    Returns:
        Structured error response
    """
    return {
        "answer": f"I encountered an issue processing your question: {error_message}. Please try rephrasing your question or check the repository path.",
        "cited_files": [],
        "related_files": [],
        "next_steps": [
            "Verify the repository path is correct",
            "Try asking a more specific question",
            "Check if the file exists in the repository"
        ],
        "confidence": 0.0,
        "query_type": query_type,
        "error": True
    }


def format_compass_response(
    orchestration_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format orchestration result into exact JSON structure for frontend
    
    Args:
        orchestration_result: Result from CompassOrchestrator
        
    Returns:
        Formatted response matching frontend requirements
    """
    return {
        "status": orchestration_result.get("status", "success"),
        "dependency_radius_score": orchestration_result.get("dependency_radius_score", 0.0),
        "learning_roadmap": orchestration_result.get("learning_roadmap", []),
        "constellation_graph": orchestration_result.get("constellation_graph", {"nodes": [], "edges": []}),
        "summary": orchestration_result.get("summary", {})
    }

# Made with Bob
