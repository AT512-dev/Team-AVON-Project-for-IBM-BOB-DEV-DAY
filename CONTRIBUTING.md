# Contributing to Compass AI

Thank you for your interest in contributing to Compass AI! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- IBM WatsonX API credentials
- Git

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Team-AVON-Project-for-IBM-BOB-DEV-DAY
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your IBM WatsonX credentials
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## 📝 Development Workflow

### Branch Naming Convention
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

Example: `feature/add-multi-language-support`

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(context): add semantic chunking for large files

- Implement AST-based code splitting
- Add relevance scoring for chunks
- Update tests for chunking module

Closes #123
```

## 🧪 Testing Guidelines

### Writing Tests
- Follow TDD (Test-Driven Development) approach
- Write behavior-focused tests, not implementation tests
- Aim for >85% code coverage
- Use descriptive test names

**Example:**
```python
def test_mentor_can_explain_file_purpose():
    """User can ask about file purpose and get cited response"""
    response = ask_mentor(
        question="What does auth.py do?",
        repo_path="/test/repo"
    )
    
    assert "auth.py" in response["answer"]
    assert len(response["cited_files"]) > 0
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_context_retrieval.py -v

# Run with coverage
pytest tests/ --cov=bob_core --cov-report=html
```

## 📚 Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all public functions

**Example:**
```python
def get_file_context(self, file_path: str) -> Optional[FileContext]:
    """
    Get complete context for a specific file.
    
    Args:
        file_path: Relative path to the file
        
    Returns:
        FileContext object or None if file not found
    """
    pass
```

### Code Formatting
```bash
# Format code with black
black bob_core/ tests/

# Check with flake8
flake8 bob_core/ tests/

# Type checking with mypy
mypy bob_core/
```

## 🔍 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests and linting**
   ```bash
   pytest tests/ -v
   black bob_core/ tests/
   flake8 bob_core/ tests/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Ensure CI passes
   - Request review from maintainers

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] PR description is clear

## 🐛 Reporting Bugs

### Bug Report Template
```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.12]
- Package version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

We welcome feature requests! Please:
1. Check if the feature already exists
2. Provide clear use case
3. Explain expected behavior
4. Consider implementation complexity

## 📖 Documentation

### Documentation Standards
- Keep README.md up to date
- Document all public APIs
- Provide code examples
- Update CHANGELOG.md

### API Documentation
- Use clear parameter descriptions
- Include request/response examples
- Document error codes
- Provide usage examples

## 🤝 Code Review Guidelines

### For Reviewers
- Be constructive and respectful
- Focus on code quality and maintainability
- Check test coverage
- Verify documentation updates

### For Contributors
- Respond to feedback promptly
- Be open to suggestions
- Ask questions if unclear
- Update PR based on feedback

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with bug template
- **Features**: Create an issue with feature template
- **Security**: Email security@example.com

## 🎓 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [IBM WatsonX Documentation](https://www.ibm.com/watsonx)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Git Workflow Guide](https://www.atlassian.com/git/tutorials/comparing-workflows)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Compass AI! 🚀**