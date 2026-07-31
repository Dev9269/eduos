# EduOS Demo Script — Faculty Review Presentation

**Duration:** 10–12 minutes  
**Presenter:** Jainam H. Maru  
**Credentials:** DEMO001 / EDUOS2026  
**VM:** Debian 13 Trixie + KDE Plasma 6, VirtualBox

---

## Step 1 — Boot & Login (30 sec)

> Boot the VM. SDDM glassmorphism theme appears.

**Narrator:** *"Welcome. This is EduOS — a purpose-built Linux distribution for engineering education, cybersecurity labs, and controlled examinations."*

**Action:** Enter `student` / the generated password (see `/etc/eduos/credentials.conf` on the installed system), press Enter.

**Check:** Smooth login, no errors. Watermark visible top-right.

---

## Step 2 — Desktop First Look (45 sec)

> Desktop loads with Windows-11 layout, taskbar, EduOS wallpaper.

**Narrator:** *"The desktop follows a familiar Windows-11 layout for zero learning curve. Students log into a branded environment with EduOS watermark, custom color scheme, and all educational tools one click away."*

**Action:** Point to taskbar icons (LearnHub, Dev Suite, Cyber Lab, Exam, Admin), open Application Launcher.

---

## Step 3 — LearnHub (1 min)

**Action:** Click LearnHub icon → browser opens at localhost:5050.

**Narrator:** *"LearnHub is the student learning management portal. Built with Flask, it provides assignments, course materials, announcements, and a schedule view — accessible from any browser on the local network."*

**Action:** Scroll through: Dashboard → Assignments → Materials → Schedule.

---

## Step 4 — Dev Suite (1 min)

**Action:** Click Dev Suite icon.

**Narrator:** *"The Developer Suite provides an integrated environment. It launches VS Code, terminal, and documentation browser side-by-side, pre-configured with Python, GCC, Git, Node.js, and SQLite."*

**Action:** Show the grid launcher; point to available tools.

---

## Step 5 — Admin Center (1 min)

**Action:** Click Admin Center icon. Password: the generated admin password from `/etc/eduos/credentials.conf`.

**Narrator:** *"The Admin Center gives faculty real-time system monitoring — CPU, memory, disk, network status, system load, and uptime. It also manages user accounts and lab network connectivity."*

**Action:** Click through tabs: Dashboard → User Management → Network.

---

## Step 6 — Demo Exam (2 min — highlight feature)

**Action:** Click Demo Exam icon on desktop.

**Narrator:** *"The Demo Exam showcases the examination system. Students authenticate with a secure access code, then proceed through a structured test with multiple-choice and coding questions."*

**Action:** Enter DEMO001 / EDUOS2026 → Instructions → Answer 2-3 MCQ → Coding challenge → Review → Submit → Show results page.

**Point out:** Results export (JSON/PDF), security logging, attempt tracking.

---

## Step 7 — Cyber Lab (2 min — live if Docker works)

**Action:** Click Cyber Lab icon.

**Narrator:** *"The Cyber Lab provides containerized cybersecurity environments. Students can spin up Kali Linux, Metasploitable, OWASP Juice Shop, and other vulnerable targets in isolated Docker containers — all from a unified interface."*

**Action:** Click "Start Juice Shop" → Docker pulls/starts container → shows terminal output → Click "Open" → browser opens Juice Shop at localhost:3000. Show the login page briefly.

---

## Step 8 — Security & Integrity (45 sec)

**Narrator:** *"EduOS is designed with security at its core. Exam sessions run in full-screen lockdown mode with keyboard shortcuts disabled. All exam data is encrypted using Fernet with PBKDF2 key derivation at 480,000 iterations. System hardening scripts lock down SSH, kernel parameters, and network services."*

**Action:** Show `/opt/eduos/` directory listing, hardening script.

---

## Step 9 — Why EduOS (30 sec — pitch close)

**Narrator:** *"EduOS replaces the need for separate Windows licenses, manual lab setup, and complex exam proctoring software. It is one unified, free, open-source platform. Built for Debian Trixie, it is stable, secure, and ready for deployment."*

---

## Step 10 — Q&A (remaining time)

**Anticipated questions:**
- *How long does ISO build take?* — 45-60 minutes, single command.
- *Can it run on existing hardware?* — Yes, any x86_64 system with 4GB RAM.
- *Is it production-ready?* — v1.0-rc1 is feature-complete; production hardening and pilot testing are next.
- *What about Windows-only EDA tools?* — Wine compatibility layer is on the roadmap.
- *How is exam integrity ensured?* — Full-screen lockdown, keyboard grab, encrypted submissions, security audit log, timer enforcement.
