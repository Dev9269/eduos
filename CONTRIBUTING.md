# Contributing to EduOS

Thank you for your interest in EduOS! This document outlines the guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive. Harassment or disruptive behavior will not be tolerated.

## How to Contribute

1. **Fork** the repository on GitHub.
2. **Create a feature branch** (`git checkout -b feature/your-feature`).
3. **Make your changes** following the project conventions.
4. **Test** your changes thoroughly.
5. **Commit** with a clear, descriptive message.
6. **Push** to your fork and open a pull request.

## Development Setup

EduOS targets FreeBSD 14.x. For local development of Python components
(works on any OS):

```bash
git clone https://github.com/Dev9269/eduos.git
cd eduos
pip install -r requirements.txt
pytest tests/ -v  # All tests should pass
```

## Code Style

- Follow PEP 8 for Python code.
- Use descriptive variable and function names.
- Keep functions focused and modular.
- Import standard library modules first, then third-party, then local.
- Maintain the existing glass UI design patterns in PyQt6 components.

## Pull Request Process

1. Ensure your PR description clearly describes the problem and solution.
2. Reference any related issues.
3. Keep PRs focused — one feature or fix per PR.
4. Update documentation and CHANGELOG.md if applicable.
5. A maintainer will review your PR and may request changes.

## Project Structure

| Directory | Contents |
|---|---|
| `AdminCenter/` | PyQt6 admin panel desktop app |
| `ExamMode/` | Secure exam application |
| `LearnHub/` | Flask student portal |
| `DevSuite/` | Dev tools launcher |
| `CyberLab/` | Containerized security labs |
| `InstitutionManager/` | Multi-institution management |
| `Server/` | FastAPI backend server |
| `Services/` | Agent daemon (Linux + FreeBSD) |
| `Scripts/` | Build and setup scripts |
| `Packages/` | FreeBSD pkg manifests + legacy Debian packages |
| `Branding/` | Themes, wallpapers, SDDM login |
| `tests/` | pytest test suite (40 tests) |

## Reporting Issues

Report bugs or suggest features via [GitHub Issues](https://github.com/Dev9269/eduos/issues).
