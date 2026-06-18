# EduOS — Faculty Funding Pitch

## One-Line Pitch
**EduOS eliminates Windows licensing costs, IT overhead, and exam security risks — replacing them with a single, free, open-source Linux distribution purpose-built for engineering education.**

---

## The Problem

| Pain Point | Cost/Impact |
|------------|-------------|
| Windows licenses per lab machine | ₹5,000–15,000/year per seat |
| Lab setup & configuration time | 2–3 weeks per semester |
| Exam security & integrity | Third-party proctoring software costs ₹200–500/student |
| Software version inconsistencies | Students using different OS/tools = grading headaches |
| IT maintenance burden | Dedicated staff for imaging, updates, troubleshooting |

## The Solution: EduOS

EduOS is a Debian 13 Trixie-based Linux distribution that ships **pre-configured** with everything an engineering lab needs:

- **Zero license cost** — 100% open source
- **One-command ISO build** — `sudo ./build-eduos-iso.sh` produces a bootable USB/DVD in ~45 minutes
- **Pre-installed tools** — Python, GCC, VS Code, Git, Node.js, SQLite, Burp Suite Community, OWASP Juice Shop, Docker
- **Integrated exam proctoring** — Full-screen lockdown, encrypted submission, timer enforcement, security audit logging
- **Cyber Lab environment** — Containerized Kali, Metasploitable, Juice Shop for hands-on security training
- **Learning management** — LearnHub portal for assignments, materials, and announcements

## Cost Comparison (30-Seat Lab Over 4 Years)

| Item | Traditional Setup | EduOS | Savings |
|------|------------------|-------|---------|
| OS licenses | ₹6,00,000 | ₹0 | ₹6,00,000 |
| Proctoring software | ₹2,40,000 | ₹0 (built-in) | ₹2,40,000 |
| IT setup time (200 hrs @ ₹500/hr) | ₹1,00,000 | ₹5,000 (one-time build) | ₹95,000 |
| Maintenance (4 yrs) | ₹3,00,000 | ₹50,000 (minimal) | ₹2,50,000 |
| **Total** | **₹12,40,000** | **₹55,000** | **₹11,85,000** |

## Technical Highlights

| Feature | Detail |
|---------|--------|
| Base OS | Debian 13 Trixie, KDE Plasma 6 |
| Security | Exam lockdown, Fernet/PBKDF2 encryption (480k iterations), SSH hardening |
| Desktop | Windows 11-style layout, glassmorphism SDDM theme |
| Portability | Single hybrid ISO (BIOS + UEFI) |
| Storage | Live USB/DVD or installed to disk |

## Current Status

- **v1.0-rc1 built and verified** — 2.3GB ISO, 320,568 files, all 53 EduOS assets verified
- **All core modules functional** — LearnHub, Exam Portal, Dev Suite, Cyber Lab, Admin Center
- **Desktop, SDDM, wallpaper, color scheme, Plymouth boot splash** — fully branded

## What Funding Enables

| Area | Use of Funds |
|------|-------------|
| Production hardening | Full security audit, penetration testing, SELinux policies |
| Pilot deployment | Hardware procurement, deployment in 1–2 labs, monitoring |
| Feature completion | Metasploit/exploitdb integration, pgAdmin4, MongoDB Shell |
| Documentation & training | Faculty training materials, student guides, video tutorials |
| CI/CD pipeline | Automated ISO builds, regression testing, update mechanism |

## Call to Action

**"Support EduOS — fund the pilot deployment and give the department a zero-license-cost, secure, modern computing lab for the next decade."**

### Investment Request

- **Phase 1 Pilot (1 lab, 30 seats):** ₹50,000
- **Phase 2 Department-wide (4 labs, 120 seats):** ₹1,50,000
- **Full adoption (all labs + faculty):** ₹3,00,000

---

**Contact:** Jainam H. Maru  
**Repository:** `/home/jainam/EduOS`  
**ISO:** `Packages/live-build/output/eduos-20260618-amd64.iso`  
**Tech Stack:** Debian 13 → KDE Plasma 6 → Python 3.13 → Flask → PyQt6 → Docker
