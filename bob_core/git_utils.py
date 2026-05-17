"""
Git utilities for cloning GitHub repositories to temporary directories
"""
import os
import tempfile
import shutil
import subprocess
from typing import Tuple
from pathlib import Path


class GitCloneError(Exception):
    """Raised when git clone operation fails"""
    pass


def clone_github_repo(github_url: str) -> Tuple[str, str]:
    """
    Clone a GitHub repository to a temporary directory.
    
    Args:
        github_url: The GitHub repository URL (e.g., https://github.com/user/repo)
        
    Returns:
        Tuple of (temp_dir_path, repo_name)
        
    Raises:
        GitCloneError: If cloning fails
        ValueError: If URL is invalid
    """
    # Validate GitHub URL
    if not github_url or not isinstance(github_url, str):
        raise ValueError("GitHub URL must be a non-empty string")
    
    if not ("github.com" in github_url.lower()):
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    
    # Extract repo name from URL
    # Handle formats: https://github.com/user/repo, https://github.com/user/repo.git
    repo_name = github_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    
    # Create temporary directory
    temp_base = tempfile.mkdtemp(prefix=f"compass_repo_{repo_name}_")
    temp_dir = os.path.join(temp_base, repo_name)
    
    try:
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", "--depth", "1", github_url, temp_dir],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise GitCloneError(
                f"Git clone failed: {result.stderr or result.stdout}"
            )
        
        # Verify the directory exists and has content
        if not os.path.isdir(temp_dir) or not os.listdir(temp_dir):
            raise GitCloneError(f"Cloned directory is empty or doesn't exist: {temp_dir}")
        
        return temp_dir, repo_name
        
    except subprocess.TimeoutExpired:
        # Cleanup on timeout
        if os.path.exists(temp_base):
            shutil.rmtree(temp_base, ignore_errors=True)
        raise GitCloneError("Git clone operation timed out after 5 minutes")
    
    except Exception as e:
        # Cleanup on any error
        if os.path.exists(temp_base):
            shutil.rmtree(temp_base, ignore_errors=True)
        raise GitCloneError(f"Failed to clone repository: {str(e)}")


def cleanup_temp_repo(repo_path: str) -> bool:
    """
    Clean up a temporary repository directory.
    
    Args:
        repo_path: Path to the temporary repository
        
    Returns:
        True if cleanup was successful, False otherwise
    """
    try:
        # Get the parent temp directory (the one created by mkdtemp)
        temp_base = os.path.dirname(repo_path)
        
        # Only delete if it looks like our temp directory
        if "compass_repo_" in os.path.basename(temp_base):
            # On Windows, we need to handle read-only files in .git directory
            def handle_remove_readonly(func, path, exc):
                """Error handler for Windows readonly files"""
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise
            
            shutil.rmtree(temp_base, onerror=handle_remove_readonly)
            return True
        return False
    except Exception:
        return False


def is_valid_github_url(url: str) -> bool:
    """
    Check if a string is a valid GitHub URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid GitHub URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    return "github.com" in url_lower and ("http://" in url_lower or "https://" in url_lower)

# Made with Bob
