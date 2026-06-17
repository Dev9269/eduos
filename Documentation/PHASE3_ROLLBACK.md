# Phase 3 — Rollback Instructions

## Files Created (new)
| File | Action to Remove |
|---|---|
| `/usr/local/bin/eduos-demo-exam` | `sudo rm -f` |
| `/usr/share/applications/eduos-demo-exam.desktop` | `sudo rm -f` |
| `/usr/share/applications/eduos-watermark.desktop` | `sudo rm -f` |
| `~/EduOS/Branding/scripts/eduos-watermark.py` | `rm -f` |
| `~/EduOS/ExamMode/demo_exam_app.py` | `rm -f` |
| `~/EduOS/ExamMode/demo_exam_config.py` | `rm -f` |
| `~/EduOS/ExamMode/DEMO_PRESENTERS_GUIDE.md` | `rm -f` |
| `~/EduOS/ExamMode/DemoResults/` (directory) | `rm -rf` |

## Autostart Entries Created
| File | Action |
|---|---|
| `/home/jainam/.config/autostart/eduos-watermark.desktop` | `rm -f` |
| `/home/student/.config/autostart/eduos-watermark.desktop` | `sudo rm -f` |
| `/home/exam/.config/autostart/eduos-watermark.desktop` | `sudo rm -f` |
| `/home/admin/.config/autostart/eduos-watermark.desktop` | `sudo rm -f` |
| `/etc/skel/.config/autostart/eduos-watermark.desktop` | `sudo rm -f` |

## CHANGELOG Backup
```bash
cp ~/EduOS/CHANGELOG.md.bak ~/EduOS/CHANGELOG.md
```

## Verification
```bash
# These should all return "No such file or directory":
ls -la /usr/local/bin/eduos-demo-exam
ls -la /usr/share/applications/eduos-demo-exam.desktop
ls -la /usr/share/applications/eduos-watermark.desktop
ls -la ~/EduOS/Branding/scripts/eduos-watermark.py
ls -la ~/EduOS/ExamMode/demo_exam_app.py
ls -la ~/home/*/.config/autostart/eduos-watermark.desktop

# Re-count desktop entries (should be 10, not 12):
ls /usr/share/applications/eduos-*.desktop | wc -l
```

## Preserved (unchanged)
- All existing user accounts and data
- System services configuration
- KDE base configuration
- All previously installed educational/security software
- Existing `exam_app.py`, `exam_admin.py` (in ExamMode/)
- Other EduOS modules (AdminCenter, LearnHub, DevSuite, CyberLab)
