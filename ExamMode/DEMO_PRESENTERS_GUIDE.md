# EduOS Demo Exam — Presenter Guide

## Purpose
This demo examination system is designed for presentations to engineering college administrators, faculty members, and university decision-makers. It demonstrates EduOS's capability to serve as a complete campus-wide examination platform.

## Quick Start

### Starting the Demo
```
eduos-demo-exam
```
Or click **EduOS Demo Exam** in the application menu (under EduOS category).

### Demo Credentials
| Field | Value |
|---|---|
| Student ID | `DEMO001` |
| Student Name | (any name for display) |
| Exam Key | `EDUOS2026` |

## Presentation Script

### Screen 1 — Login (30 seconds)
- Show the professional login interface
- Enter DEMO001 / EDUOS2026
- Highlight: branded look, simple UX, demo-ready

### Screen 2 — Instructions (30 seconds)
- Overview of exam structure: 10 MCQ + 1 Coding challenge
- 30-minute timer, auto-save, auto-submit
- Highlight: clear instructions, timer display

### Screen 3 — MCQ Section (2-3 minutes)
- Navigate through questions using the palette
- Point out: question palette with answered/unanswered status
- Show: timer countdown, progress bar
- Demonstrate: selecting answers, auto-save
- Highlight: professional UI, no distractions

### Screen 4 — Coding Section (2-3 minutes)
- Switch between Python / C / C++ / Java
- Type a simple palindrome solution to demonstrate live execution
- Show: Run Code button executing locally
- Highlight: syntax highlighting, multi-language support, local sandboxed execution

### Screen 5 — Review Screen (30 seconds)
- Show summary of MCQ + Coding sections
- Confirm submission

### Screen 6 — Results (1 minute)
- Display score with pass/fail status
- Export to **JSON**
- Export to **PDF** (saved to `~/EduOS/ExamMode/DemoResults/`)
- Highlight: instant results, portable formats

### Anti-Cheating Demo (1 minute)
- Try Alt+Tab → blocked and logged
- Try Ctrl+C during exam → blocked
- Try Escape → exit warning dialog
- Check security log: `cat ~/EduOS/ExamMode/DemoResults/security_log.txt`
- Highlight: exam integrity without kernel-level modifications

## Key Talking Points

### For Administrators
- **Zero infrastructure**: Runs on any EduOS machine, no servers needed
- **Offline**: Full exam capability without internet
- **Secure**: Encrypted storage, anti-cheating, restricted exam sessions
- **Scalable**: Can be deployed across entire lab with Admin Center

### For Faculty
- **Easy to set up**: Create exams in minutes
- **Auto-graded**: MCQ is instant, coding can be manually reviewed
- **Results**: JSON for analysis, PDF for records
- **Student-friendly**: Familiar interface, clear navigation, timer warnings

### For IT/Technical Staff
- **Docker-based isolation**: CyberLab runs in --network=none containers
- **Python/PyQt6 stack**: Easy to customize, extend, maintain
- **Open source**: MIT licensed
- **Modular**: Each component is independent

## Demo Reset
To reset demo data and re-run:
```bash
rm -rf ~/EduOS/ExamMode/DemoResults/
eduos-demo-exam
```

## System Requirements
- EduOS (Debian 13 Trixie, KDE Plasma)
- Python 3.13+
- PyQt6 (python3-pyqt6)
- reportlab (python3-reportlab) — for PDF export
- GCC/G++ — for C/C++ code execution
- OpenJDK 21 — for Java code execution

All dependencies are pre-installed in EduOS.

## Technical Architecture
```
demo_exam_app.py          — Main application (6 screens, anti-cheat, export)
demo_exam_config.py       — Question bank, exam config, credentials
~/EduOS/ExamMode/DemoResults/
  ├── result_*.json       — JSON export of results
  ├── result_*.pdf        — PDF export of results
  ├── coding_draft_*.txt  — Auto-saved coding drafts
  └── security_log.txt    — Anti-cheating attempt log
```

## Known Limitations (Demo Only)
1. MCQ questions are hardcoded — production would load from a database
2. Coding challenges are single-question — production would have multiple
3. Anti-cheating blocks standard shortcuts but advanced users can bypass (no kernel hooks)
4. Results are local-only — production would sync to a central server
5. No question bank randomization — all students see same order
6. PDF export requires reportlab (pre-installed)

## Evolving to Production
For a production university examination system:
1. Centralized exam server with PostgreSQL backend
2. Dynamic question loading from database with randomization
3. Per-student question ordering to prevent cheating
4. Real-time proctoring dashboard in Admin Center
5. LMS integration (Moodle, Canvas API sync)
6. Biometric or smart-card authentication
7. Network-based exam distribution to lab machines
8. Results aggregation and analytics dashboard
