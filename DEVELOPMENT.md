# Development Guide

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Dev9269/eduos.git
cd eduos

# Install Python dependencies
pip install -r requirements.txt

# Run individual modules
python LearnHub/learnhub_app.py    # Learning portal (Flask, port 5050)
python ExamMode/exam_app.py        # Exam application (PyQt6)
python AdminCenter/eduos_admin.py  # Admin console (PyQt6)
```

## Running on FreeBSD

EduOS targets FreeBSD 14.x. The agent runs as an rc.d service:

```sh
# Enable and start the agent on a student PC
sudo cp Services/freebsd/eduos_agent /usr/local/etc/rc.d/eduos_agent
sudo chmod +x /usr/local/etc/rc.d/eduos_agent
sudo sysrc eduos_agent_enable=YES
sudo service eduos_agent start

# Check status / stop
sudo service eduos_agent status
sudo service eduos_agent stop

# Server on the admin laptop (no rc.d needed — run via script)
bash Server/start-server.sh
```

## Project Structure

| Directory | Purpose | Tech |
|-----------|---------|------|
| `LearnHub/` | Learning portal | Flask + SQLite |
| `ExamMode/` | Secure exam app | PyQt6 + Cryptography |
| `AdminCenter/` | Administration console | PyQt6 |
| `DevSuite/` | Dev environment launcher | PyQt6 |
| `CyberLab/` | Security lab manager | PyQt6 + Podman/Docker |
| `Scripts/` | System tools | Shell |
| `Branding/` | Logo, wallpaper, themes | Assets |
| `Packages/` | FreeBSD pkg manifests | FreeBSD pkg |

## Code Style

- Python: PEP 8, type hints encouraged
- PyQt6: Follow existing glass UI design patterns
- Shell: Use `sh`-validated constructs (FreeBSD `/bin/sh`)

## Building

```bash
# Run all tests
make test

# Lint code
make lint

# Validate YAML, shell, and Python syntax
make validate

# Create distribution package
make build

# Trigger FreeBSD ISO build via GitHub Actions
make build-freebsd-iso
```

See the [Makefile](Makefile) for all available targets.
