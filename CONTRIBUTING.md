# Contributing to Scoliosis Brace Coach AI

Thank you for your interest in contributing! This project helps parents and clinicians monitor scoliosis treatment progress using AI pose estimation.

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/srinathsankara/scoliosis-brace-coach/issues) to avoid duplicates
2. Open a new issue using the **Bug Report** template
3. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Python version and OS

### Suggesting Features

1. Open an issue using the **Feature Request** template
2. Describe the problem your feature would solve
3. Include use cases and expected behavior

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `python tests/run_all_tests.py`
5. Commit with a clear message: `git commit -m "Add: description of change"`
6. Push and open a Pull Request

### Development Setup

```bash
git clone https://github.com/srinathsankara/scoliosis-brace-coach.git
cd scoliosis-brace-coach
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
python app.py
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for public functions
- Keep functions focused and under 50 lines
- No hardcoded secrets or credentials

### Testing

- Write unit tests for new analysis rules
- Add integration tests for new API endpoints
- Include security tests for user-facing inputs
- Run the full suite before submitting PRs

### Medical Disclaimer

All contributions must maintain the existing medical disclaimer. This application is for educational and monitoring purposes only. Contributors must not add code that could be interpreted as providing medical diagnosis or treatment recommendations.

## Code of Conduct

Be respectful, inclusive, and constructive. We're building something that helps families manage a medical condition.

## Questions?

Open a [Discussion](https://github.com/srinathsankara/scoliosis-brace-coach/discussions) for general questions.
