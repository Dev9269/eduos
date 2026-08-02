# EduOS — Remaining Tasks & Roadmap

**Last updated:** August 2026 (after Phase 9)

## Done ✅ (Phases 1–9)

- FreeBSD ISO build pipeline (GitHub Actions)
- FastAPI server with JWT auth, rate limiting
- Agent daemon (FreeBSD rc.d + Linux systemd)
- Exam Mode with lockdown (keyboard block, clipboard clear, USB lock)
- Admin panel (device management, exam scheduling, roster, updates)
- Student roster validation before exam entry
- Exam submission API with checksum verification
- Code similarity checker (Jaccard n-gram)
- Update push + rollback system
- End-to-end test suite (60+ tests)
- PDF result slips after exam submission
- LearnHub ↔ server sync
- Offline package cache for campus deployment
- bcrypt authentication in api_server
- All 4 service daemons fixed (no more hardcoded external URLs)
- QEMU boot test script (Scripts/test-freebsd-iso.sh)
- Settings app (system info + server connection)
- Exam question builder in admin panel
- Desktop notifications (broadcast + exam warning)

## In Progress ⚠

- QEMU boot verification of the actual CI-built ISO
- SQLite encryption at rest (planned)
- KDE Plasma first-login auto-configuration on FreeBSD

## Planned 🔲 (Phase 10+)

- [ ] QEMU boot test script in CI
- [ ] SQLite database encryption (SQLCipher)
- [ ] Student ID card integration (NFC/barcode scan)
- [ ] Attendance system integration
- [ ] Plagiarism check dashboard in admin panel
- [ ] AI-powered grading assistant
- [ ] Multi-campus deployment (multiple server nodes)
- [ ] FreeBSD custom kernel with EduOS branding (v3.0)
- [ ] Mobile app for students (iOS/Android)
- [ ] Faculty portal (separate from admin)
