"""
Test script to verify GitHub URL cloning integration
"""
import asyncio
import sys
import os
import pytest

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from bob_core.git_utils import clone_github_repo, cleanup_temp_repo, is_valid_github_url, GitCloneError


def test_url_validation():
    """Test GitHub URL validation"""
    print("Testing URL validation...")
    
    # Valid URLs
    assert is_valid_github_url("https://github.com/user/repo") == True
    assert is_valid_github_url("http://github.com/user/repo") == True
    assert is_valid_github_url("https://github.com/user/repo.git") == True
    
    # Invalid URLs
    assert is_valid_github_url("not a url") == False
    assert is_valid_github_url("") == False
    assert is_valid_github_url(None) == False
    assert is_valid_github_url("https://gitlab.com/user/repo") == False
    
    print("[PASS] URL validation tests passed")


def test_clone_and_cleanup():
    """Test cloning a small public repository"""
    print("\nTesting repository cloning...")
    
    # Use a small, well-known public repository
    test_url = "https://github.com/octocat/Hello-World"
    
    try:
        # Clone the repository
        print(f"Cloning {test_url}...")
        temp_path, repo_name = clone_github_repo(test_url)
        
        print(f"[PASS] Successfully cloned to: {temp_path}")
        print(f"[PASS] Repository name: {repo_name}")
        
        # Verify the directory exists
        assert os.path.isdir(temp_path), "Cloned directory doesn't exist"
        assert os.listdir(temp_path), "Cloned directory is empty"
        print(f"[PASS] Directory exists and contains files")
        
        # Test cleanup
        print("Testing cleanup...")
        cleanup_result = cleanup_temp_repo(temp_path)
        assert cleanup_result == True, "Cleanup failed"
        assert not os.path.exists(temp_path), "Directory still exists after cleanup"
        print("[PASS] Cleanup successful")
        
    except GitCloneError as e:
        pytest.skip(f"Skipping live GitHub clone test: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")


def test_invalid_url_handling():
    """Test handling of invalid URLs"""
    print("\nTesting invalid URL handling...")
    
    invalid_url = "https://github.com/nonexistent/repo-that-does-not-exist-12345"
    
    try:
        clone_github_repo(invalid_url)
        pytest.fail("Should have raised GitCloneError")
    except GitCloneError as e:
        print(f"[PASS] Correctly raised GitCloneError: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error type: {e}")


@pytest.mark.asyncio
async def test_api_request_format():
    """Test that the API request format matches expectations"""
    print("\nTesting API request format...")
    
    from bob_core.main import OnboardRequest, CompassAnalysisRequest, AskRequest
    
    # Test OnboardRequest
    onboard_req = OnboardRequest(
        github_url="https://github.com/user/repo",
        task_description="Test task"
    )
    assert hasattr(onboard_req, 'github_url'), "OnboardRequest missing github_url"
    assert onboard_req.github_url == "https://github.com/user/repo"
    print("[PASS] OnboardRequest format correct")
    
    # Test CompassAnalysisRequest
    compass_req = CompassAnalysisRequest(
        github_url="https://github.com/user/repo",
        task_description="Test task",
        max_roadmap_files=10,
        include_tests=False
    )
    assert hasattr(compass_req, 'github_url'), "CompassAnalysisRequest missing github_url"
    assert compass_req.github_url == "https://github.com/user/repo"
    print("[PASS] CompassAnalysisRequest format correct")
    
    # Test AskRequest
    ask_req = AskRequest(
        github_url="https://github.com/user/repo",
        question="What does this code do?"
    )
    assert hasattr(ask_req, 'github_url'), "AskRequest missing github_url"
    assert ask_req.github_url == "https://github.com/user/repo"
    print("[PASS] AskRequest format correct")


def main():
    """Run all tests"""
    print("=" * 60)
    print("GitHub Integration Tests")
    print("=" * 60)
    
    try:
        # Run synchronous tests
        test_url_validation()
        test_clone_and_cleanup()
        test_invalid_url_handling()
        
        # Run async tests
        asyncio.run(test_api_request_format())
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        print("\nBackend is ready to accept GitHub URLs from the frontend.")
        print("Frontend should send requests with 'github_url' parameter.")
        
    except Exception as e:
        print(f"\n[FAIL] Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
