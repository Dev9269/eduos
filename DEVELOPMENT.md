# Development Guide

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Dev9269/eduos.git
cd eduos

# Install Python dependencies
pip install -r requirements.txt

# Run individual modules
python LearnHub/app.py        # Learning portal (Flask)
python ExamMode/main.py       # Exam application (PyQt6)
python AdminCenter/main.py    # Admin console (PyQt6)
```

## Project Structure

| Directory | Purpose | Tech |
|-----------|---------|------|
| `LearnHub/` | Learning portal | Flask + SQLite |
| `ExamMode/` | Secure exam app | PyQt6 + Cryptography |
| `AdminCenter/` | Administration console | PyQt6 |
| `DevSuite/` | Dev environment launcher | PyQt6 |
| `CyberLab/` | Security lab manager | PyQt6 + Docker |
| `Scripts/` | System tools | Bash |
| `Branding/` | Logo, wallpaper, themes | Assets |

## Code Style

- Python: PEP 8, type hints encouraged
- PyQt6: Follow existing glass UI design patterns
- Bash: Use shellcheck-validated constructs

## Building

```bash
# Run all tests
make test

# Lint code
make lint

# Build system ISO
sudo make build-iso

# Apply hardening
sudo make hardening
```

See the [Makefile](Makefile) for all available targets.
