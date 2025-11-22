# Contributing to AgentScope Local

Thank you for your interest in contributing to AgentScope Local! We welcome contributions from the community.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/AgentScopeLocal
   cd AgentScopeLocal
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .[dev]
   ```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentscope

# Run specific test file
pytest tests/unit/test_session.py
```

## 🎨 Code Style

We use `black` for formatting and `ruff` for linting:

```bash
# Format code
black .

# Check linting
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

## 📝 Submitting Changes

1. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**

   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Tests and Linting**

   ```bash
   pytest
   black .
   ruff check .
   ```

4. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):

   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test changes
   - `refactor:` - Code refactoring
   - `chore:` - Build/tooling changes

5. **Push and Create PR**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a Pull Request on GitHub.

## 🐛 Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

Include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version)
- Relevant logs or screenshots

## 💡 Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

## 📚 Documentation

- Update the README if you change user-facing features
- Add docstrings to new functions/classes
- Update examples if needed

## ✅ Pull Request Checklist

- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Code formatted with `black`
- [ ] Linting passes (`ruff check`)
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits

## 🤝 Code of Conduct

Please be respectful and constructive. We're all here to build something great together!

## 💬 Questions?

- Open a [Discussion](https://github.com/yagna-1/AgentScopeLocal/discussions)
- Check existing [Issues](https://github.com/yagna-1/AgentScopeLocal/issues)

Thank you for contributing! 🎉
