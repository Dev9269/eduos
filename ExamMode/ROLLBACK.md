# Phase 3 — Rollback Instructions

## Prerequisite
Before making any changes in this phase, the following backups were created:
- `~/EduOS/ExamMode/demo_exam_app.py` (no prior file — newly created)
- `~/EduOS/ExamMode/demo_exam_config.py` (no prior file — newly created)

## Rollback Steps

### 1. Remove Demo Exam Application
```bash
rm -f /usr/local/bin/eduos-demo-exam
rm -f /usr/share/applications/eduos-demo-exam.desktop
rm -f ~/EduOS/ExamMode/demo_exam_app.py
rm -f ~/EduOS/ExamMode/demo_exam_config.py
rm -rf ~/EduOS/ExamMode/DemoResults/
rm -f ~/EduOS/ExamMode/DEMO_PRESENTERS_GUIDE.md
```

### 2. Remove Watermark
```bash
rm -f /usr/share/applications/eduos-watermark.desktop
rm -f /home/jainam/.config/autostart/eduos-watermark.desktop
rm -f /home/student/.config/autostart/eduos-watermark.desktop
rm -f /home/exam/.config/autostart/eduos-watermark.desktop
rm -f /home/admin/.config/autostart/eduos-watermark.desktop
sudo rm -f /etc/skel/.config/autostart/eduos-watermark.desktop
rm -f ~/EduOS/Branding/scripts/eduos-watermark.py
```

### 3. Restore Previous CHANGELOG
```bash
cp ~/EduOS/CHANGELOG.md.bak ~/EduOS/CHANGELOG.md
```

### 4. Verify Rollback
Check that removed items are gone:
```bash
ls /usr/local/bin/eduos-demo-exam 2>/dev/null && echo "STILL EXISTS" || echo "REMOVED"
ls /usr/share/applications/eduos-*.desktop 2>/dev/null | wc -l
```

### 5. Plasma Desktop Restart (if watermark still showing)
```bash
kquitapp6 plasmashell && kstart6 plasmashell
```

## No Changes Made To:
- Existing user accounts (jainam, student, exam, admin)
- Home directory contents and permissions
- System services (UFW, SSH, etc.)
- Existing educational/security software
- KDE Plasma desktop base configuration
- Existing exam_app.py, exam_admin.py (preserved)
- Other EduOS modules (AdminCenter, LearnHub, DevSuite, CyberLab)
