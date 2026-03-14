# Contributing to Publish-Socials

Thank you for considering contributing to Publish-Socials! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Adding New Platforms](#adding-new-platforms)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful in all interactions and follow common courtesy when participating in this project.

## How to Contribute

There are many ways to contribute to Publisher:

- Report bugs and suggest features
- Improve documentation
- Write tests
- Add support for new platforms
- Fix bugs
- Improve code quality

## Development Setup

1. **Fork the repository** and clone it locally:
   ```bash
   git clone https://github.com/299-Labs/Publish-Socials.git
   cd Publish-Socials
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   pip install -r dev-requirements.txt  # If you create this file
   ```

4. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Testing

We use `pytest` for testing. To run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=publish_socials --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

When adding new features or fixing bugs, please include tests:

1. **Unit tests**: Test individual functions and classes
2. **Integration tests**: Test interactions between components
3. **Mock external dependencies**: Use `unittest.mock` for API calls

Example test structure:
```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Code Style

We follow PEP 8 and use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Running Code Quality Tools

```bash
# Format code with Black
black tests/

# Sort imports with isort
isort tests/

# Lint with flake8
flake8 tests/

# Type checking with mypy
mypy ./
```

### Pre-commit Hooks

We recommend setting up pre-commit hooks to automatically run code quality checks:

```bash
pre-commit install
```

This will automatically format and lint your code before each commit.

## Submitting Changes

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and write tests.

3. **Run tests and linting**:
   ```bash
   pytest
   black publish_socials/ tests/
   flake8 publish_socials/ tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub.

### Publishing Releases

This project uses OpenID Connect (OIDC) for secure, credential-free publishing to PyPI:

**For Maintainers:**
- No API tokens or credentials required for PyPI publishing
- Releases are automatically published when GitHub releases are created
- Uses GitHub's OIDC integration with PyPI for security

**Release Process:**
1. Update version in `pyproject.toml`
2. Create and push git tag: `git tag v1.0.1 && git push origin v1.0.1`
3. Create GitHub release for the tag
4. PyPI package is automatically published via GitHub Actions

### Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add support for new platform

- Implement platform-specific publisher
- Add configuration options
- Include comprehensive tests

Closes #123
```

## Adding New Platforms

To add support for a new platform:

1. **Create platform module**: `publish_socials/platforms/newplatform_publisher.py`
2. **Implement required methods**:
   - `__init__(self, config)`
   - `publish(self, article)`
   - `is_connected(self)`
   - `test_connection(self)`
3. **Add configuration**: Update `config.py` with required fields
4. **Update main publisher**: Import and initialize in `publish_socials.py`
5. **Write tests**: Create comprehensive tests in `tests/`
6. **Update documentation**: Add platform to README

Example platform implementation:
```python
class NewPlatformPublisher:
    def __init__(self, config):
        self.config = config
        # Initialize platform-specific settings
    
    def publish(self, article):
        # Implement publishing logic
        pass
    
    def is_connected(self):
        # Check connection status
        pass
    
    def test_connection(self):
        # Test platform connection
        pass
```

## Reporting Bugs

When reporting bugs, please include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs **actual behavior**
4. **Environment details**:
   - Python version
   - Operating system
   - Publisher version
5. **Error messages** and stack traces (if applicable)
6. **Minimal reproducible example** (if possible)

## Feature Requests

To request new features:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (if you have ideas)
   - Examples of how it would work

## Development Workflow

We follow a standard GitHub workflow:

1. **Issue**: Create or find an existing issue
2. **Branch**: Create feature branch from `develop`
3. **Code**: Implement changes with tests
4. **Test**: Ensure all tests pass
5. **PR**: Create pull request to `develop` branch
6. **Review**: Address review feedback
7. **Merge**: PR merged by maintainer

## Getting Help

- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README and inline documentation

## Code Review Process

All changes go through code review:

- **Automated checks**: CI/CD pipeline runs tests and linting
- **Manual review**: Maintainers review code quality and functionality
- **Feedback**: Address reviewer comments and suggestions
- **Approval**: Changes must be approved before merging

## Security

If you discover a security vulnerability:

1. **Do not open a public issue**
2. **Contact us privately** at contact@299labs.com
3. **Include details** about the vulnerability
4. **We will respond** within 48 hours

## Questions?

If you have questions about contributing, please:

- Open a GitHub issue with the `question` label
- Join our discussions
- Check the documentation

Thank you for contributing to Publish-Socials! 🎉