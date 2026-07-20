# Security Policy

## Reporting a Vulnerability

EduOS takes security seriously. If you discover a security vulnerability, please report it privately.

**Do not report security issues via public GitHub issues.** Instead, email the maintainer directly at **jainam@dev9269.dev** (or the contact listed in the commit history).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Affected versions/components
- Any potential impact

You will receive a response within 72 hours. We ask that you give us up to 30 days to address the issue before any public disclosure.

## Scope

- The EduOS Python applications (ExamMode, AdminCenter, LearnHub, etc.)
- System scripts and hardening configurations
- Network services and daemons

## Out of Scope

- Dependencies and third-party packages (report those upstream)
- Theoretical vulnerabilities without a working proof of concept

## Security Features

- Fernet encryption + PBKDF2 key derivation for exam submissions
- Lockdown mode restricts network, screenshots, and terminal during exams
- UFW firewall with default deny rules
- Process accounting and audit trails
- CyberLab containers isolated from the host network

## Supported Versions

Only the latest commit on the `main` branch receives security patches. Always update to the latest version.
