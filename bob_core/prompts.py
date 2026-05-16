"""
Enhanced Mentor Prompt System for IBM Bob
Transforms generic prompts into context-aware, mentor-like guidance
"""

from typing import Dict, List, Optional, Any


# Base mentor persona - constant across all queries
BASE_MENTOR_PROMPT = """You are a senior technical mentor for the {repo_name} codebase.

Your role:
- Guide new developers through the codebase architecture
- Explain file purposes and relationships in plain English
- Recommend learning paths based on complexity and dependencies
- Cite specific files when explaining concepts
- Warn about architectural impacts of changes

Your knowledge:
- Complete file tree and import graph
- Dependency complexity scores (Easy/Medium/Hard)
- Which files are central vs peripheral
- Common entry points and data flow

Response style:
- Concise and practical (2-3 paragraphs max)
- Always cite specific files using format: `filename.ext`
- Use analogies when explaining complex patterns
- Prioritize actionable guidance over theory
"""


# Query-specific templates for different question types
QUERY_TEMPLATES = {
    "file_purpose": """
Repository Context:
{repo_structure}

File in Question: {file_path}
Imports: {imports}
Imported By: {imported_by}
Complexity: {complexity}

Question: {user_question}

Explain this file's purpose, its role in the system, and which files depend on it.
""",
    
    "where_to_start": """
Repository Context:
{repo_structure}

Task: {task_description}

Available Files (sorted by learning order):
{ranked_files}

Question: {user_question}

Recommend which files to study first and why, considering complexity and centrality.
""",
    
    "impact_analysis": """
Repository Context:
{repo_structure}

File to Modify: {file_path}
Direct Dependencies: {direct_deps}
Reverse Dependencies: {reverse_deps}

Question: {user_question}

Explain what would break if this file is modified, and which tests should be updated.
""",
    
    "general": """
Repository Context:
{repo_structure}

Current Focus: {current_file}

Question: {user_question}

Answer based on the repository structure and file relationships.
"""
}


def build_mentor_prompt(
    query_type: str,
    repo_context: Dict[str, Any],
    user_question: str,
    **kwargs
) -> str:
    """
    Build context-aware prompt for IBM Bob
    
    Args:
        query_type: Type of query (file_purpose, where_to_start, impact_analysis, general)
        repo_context: Repository information (name, files, structure)
        user_question: The user's question
        **kwargs: Additional context variables (file_path, imports, complexity, etc.)
    
    Returns:
        Complete prompt string ready for WatsonX API
    """
    # Build base prompt with repo name
    repo_name = repo_context.get("name", "this project")
    base = BASE_MENTOR_PROMPT.format(repo_name=repo_name)
    
    # Select appropriate template
    template = QUERY_TEMPLATES.get(query_type, QUERY_TEMPLATES["general"])
    
    # Prepare context variables
    context_vars = {
        "repo_structure": format_repo_structure(repo_context),
        "user_question": user_question,
        **kwargs
    }
    
    # Fill in missing optional parameters with defaults
    context_vars.setdefault("file_path", "N/A")
    context_vars.setdefault("imports", [])
    context_vars.setdefault("imported_by", [])
    context_vars.setdefault("complexity", "Unknown")
    context_vars.setdefault("current_file", "N/A")
    context_vars.setdefault("task_description", "Understanding the codebase")
    context_vars.setdefault("ranked_files", "")
    context_vars.setdefault("direct_deps", [])
    context_vars.setdefault("reverse_deps", [])
    
    # Format lists as strings
    if isinstance(context_vars["imports"], list):
        context_vars["imports"] = ", ".join(context_vars["imports"]) if context_vars["imports"] else "None"
    if isinstance(context_vars["imported_by"], list):
        context_vars["imported_by"] = ", ".join(context_vars["imported_by"]) if context_vars["imported_by"] else "None"
    if isinstance(context_vars["direct_deps"], list):
        context_vars["direct_deps"] = ", ".join(context_vars["direct_deps"]) if context_vars["direct_deps"] else "None"
    if isinstance(context_vars["reverse_deps"], list):
        context_vars["reverse_deps"] = ", ".join(context_vars["reverse_deps"]) if context_vars["reverse_deps"] else "None"
    
    # Build query-specific prompt
    query_prompt = template.format(**context_vars)
    
    # Combine base + query-specific
    return f"{base}\n\n{query_prompt}"


def format_repo_structure(repo_context: Dict[str, Any]) -> str:
    """
    Format repository structure for inclusion in prompts
    
    Args:
        repo_context: Dictionary containing repository information
    
    Returns:
        Formatted string representation of repo structure
    """
    files = repo_context.get("files", {})
    
    if not files:
        return "Repository structure not available"
    
    # Create a concise summary
    total_files = len(files)
    file_list = list(files.keys())[:10]  # Show first 10 files
    
    structure = f"Total files: {total_files}\n"
    structure += "Key files:\n"
    
    for file_path in file_list:
        imports = files.get(file_path, [])
        import_count = len(imports) if isinstance(imports, list) else 0
        structure += f"  - {file_path} (imports: {import_count})\n"
    
    if total_files > 10:
        structure += f"  ... and {total_files - 10} more files\n"
    
    return structure


def classify_query(question: str) -> str:
    """
    Classify question type for appropriate prompt template
    
    Args:
        question: User's question
    
    Returns:
        Query type: file_purpose, where_to_start, impact_analysis, or general
    """
    question_lower = question.lower()
    
    # File purpose queries
    if any(word in question_lower for word in ["what does", "what is", "purpose", "role", "responsibility"]):
        return "file_purpose"
    
    # Where to start queries
    elif any(word in question_lower for word in ["where to start", "where should i", "begin", "first", "start with"]):
        return "where_to_start"
    
    # Impact analysis queries
    elif any(word in question_lower for word in ["break", "impact", "modify", "change", "affect", "what if"]):
        return "impact_analysis"
    
    # Default to general
    else:
        return "general"


def format_ranked_files(files_with_scores: List[Dict[str, Any]]) -> str:
    """
    Format ranked files for where_to_start queries
    
    Args:
        files_with_scores: List of dicts with file_path, complexity, centrality
    
    Returns:
        Formatted string of ranked files
    """
    if not files_with_scores:
        return "No files available"
    
    result = []
    for i, file_info in enumerate(files_with_scores[:10], 1):
        file_path = file_info.get("file_path", "unknown")
        complexity = file_info.get("complexity", "Unknown")
        centrality = file_info.get("centrality", 0)
        
        result.append(f"{i}. {file_path} (Complexity: {complexity}, Importance: {centrality:.2f})")
    
    return "\n".join(result)

# Made with Bob
