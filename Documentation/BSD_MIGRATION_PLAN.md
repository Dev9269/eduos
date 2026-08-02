# EduOS BSD Migration Plan

## Current Migration Status (August 2026)

| Phase | Status |
|---|---|
| Phase 1: Keep Debian base, isolate proprietary code | ✅ COMPLETE |
| Phase 2: FreeBSD ISO build pipeline | ✅ COMPLETE (build-freebsd-iso.yml) |
| Phase 2: FreeBSD rc.d agent service | ✅ COMPLETE (Services/freebsd/) |
| Phase 2: FreeBSD desktop setup script | ✅ COMPLETE (Scripts/freebsd-desktop-setup.sh) |
| Phase 3: FreeBSD custom kernel branding | 🔲 PLANNED |

---

> **Decision (locked):** Hybrid approach for the current stage.
> Keep the Debian base, isolate all proprietary EduOS components into a
> clearly-bounded closed-source layer. Full FreeBSD migration is planned
> for v2.0 (Phase 2 below).

---

## 1. Why BSD over Linux for proprietary licensing

- **Linux kernel = GPL v2** — forces source disclosure of the kernel and,
  for derivative distributions, creates strong pressure to open the whole
  stack.
- **FreeBSD kernel = BSD license** — allows closed-source, proprietary
  products without any source disclosure obligation.
- This is why major commercial operating systems choose BSD derivatives
  instead of Linux:
  - Sony PlayStation OS → FreeBSD
  - Apple macOS / iOS → Darwin (BSD derivative)
  - Nintendo Switch OS → FreeBSD
  - NetApp, Juniper, WhatsApp infrastructure → FreeBSD

For EduOS, which the owner wants to keep partially proprietary
(ExamMode, AdminCenter, AgentDaemon, InstitutionManager), a BSD base
removes the licensing conflict entirely.

## 2. Candidate evaluation

| Criterion | FreeBSD | NetBSD | OpenBSD |
|---|---|---|---|
| Completeness | Best — full desktop support via `pkg` | Good | Minimal |
| Hardware support | Best among BSDs (laptops, GPUs, Wi-Fi) | Good (many old platforms) | Limited |
| Security posture | Good | Good | Best (defaults hardened) |
| Desktop (KDE Plasma) | Available via `pkg` | Available | Not practical |
| NVIDIA/AMD drivers | Available | Limited | Limited |
| Community/maintenance | Largest BSD community | Small | Small |
| Suitability for lab desktops | **Excellent** | Poor | Poor |

**Recommendation: FreeBSD.** It is the only BSD with realistic support
for KDE Plasma desktop labs, modern laptop hardware, and a large enough
software repository (`pkg`) to cover the EduOS application stack.

## 3. Current stage: Hybrid approach (implemented now)

Full BSD migration is **not feasible at this stage** — the entire build
toolchain (bsdinstall, makefs/mkimg build, apt packages, KDE Plasma packaging)
is Debian-specific. Ripping out the base would stall all current work.

Therefore, until v2.0:

1. **Keep the Debian/Live-build base** — everything continues to build
   and boot as today.
2. **Isolate proprietary components** into a clearly-bounded closed-source
   layer:
   - `ExamMode/` — exam lockdown + encryption
   - `AdminCenter/` — admin console
   - `Services/eduos-agent.py` — student-PC agent daemon
   - `Server/eduos_server.py` — admin broker server
   - `InstitutionManager/` — institution administration
3. **Documented boundary:** the closed-source layer only talks to the
   open base through:
   - systemd unit files (`Services/*.service`)
   - the WebSocket protocol (`ws://server:8765/ws/agent`)
   - `/etc/eduos/` config files
   - UFW firewall rules
4. This boundary means the proprietary layer can later be released as
   private Debian packages (or BSD packages) without the open base being
   affected.

## 4. Migration path

### Phase 1 (current) — Debian base + isolated proprietary layer
- Everything builds with `Scripts/build-iso.sh` / makefs/mkimg build.
- Proprietary components in their own directories, no GPL coupling.
- Document the boundary (this file).

### Phase 2 (v2.0) — Port to FreeBSD base
- Replace `bsdinstall`/makefs/mkimg build with FreeBSD base system + `pkg`.
- Use FreeBSD's `mkisofs`/`makefs` for ISO generation or
  `buildiso` ports infrastructure.
- Install KDE Plasma via `pkg install plasma6-plasma-desktop sddm`.

### Phase 3 (v3.0) — Custom FreeBSD-derived kernel
- Take the FreeBSD kernel sources (BSD-licensed) and add EduOS branding
  and custom scheduling/security modules.
- Release binaries without source disclosure obligation.

## 5. Key differences to handle in the port

| Concern | Debian (now) | FreeBSD (target) |
|---|---|---|
| Init/service manager | systemd | `rc.d` scripts or OpenRC |
| Package manager | `apt` / dpkg | `pkg` |
| Version file | `/etc/debian_version` | `/etc/freebsd-version` |
| Firewall | `ufw` | `pf` (built-in, also an IPS) |
| User management | `useradd`/`passwd` | `pw` |
| Filesystem | ext4 | ZFS (snapshots, compression) |
| Kernel modules | DKMS | kld / modules |
| Desktop | KDE Plasma (apt) | KDE Plasma (`pkg install plasma6-plasma-desktop`) |
| Python | system python3 + pip | system python3 + pip (same) |

## 6. What stays the same

- All Python application code (PyQt6, FastAPI, agent daemons)
- All exam mode logic (ExamMode)
- All admin panel logic (AdminCenter)
- All WebSocket communication (Server ↔ Agent)
- SQLite database schemas
- The `.eduos/` config layout

The Python stack is identical on FreeBSD, which is what makes this
migration feasible at all — the port effort is concentrated in the
build system, init scripts, and packaging, not in the application code.

## 7. License boundary summary (Phase 1)

| Layer | Contents | License |
|---|---|---|
| Open base | makefs/mkimg build config, scripts, themes, branding assets, docs | GPL-compatible (OS components) |
| Closed layer | ExamMode, AdminCenter, Services/eduos-agent.py, Server/, InstitutionManager | Proprietary — not shipped in source form |
| Boundary | systemd units, WebSocket protocol, `/etc/eduos/*.conf`, firewall rules | Documented in ARCHITECTURE.md + this file |

Once on FreeBSD (Phase 2+), the "open base" layer also moves to a
permissive (BSD) license, eliminating the GPL obligations entirely.
