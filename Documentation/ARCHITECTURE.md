# EduOS v3.0 Architecture

> Version 3.0 | July 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Three-Layer Architecture](#three-layer-architecture)
3. [System Boot Flow](#system-boot-flow)
4. [Security Architecture](#security-architecture)
5. [Exam Data Flow](#exam-data-flow)
6. [Update Flow](#update-flow)
7. [Network Topology](#network-topology)
8. [Database Schema](#database-schema)
9. [Component Relationships](#component-relationships)

---

## Overview

EduOS v3.0 is built on a modern three-tier architecture that separates concerns across administrative domains. The system is designed for scalability, security, and ease of management across thousands of educational institutions.

### Design Principles

- **Defense in Depth** — Multiple layers of security at every level
- **Least Privilege** — Role-based access with minimal permissions
- **Modularity** — Independent components communicating through well-defined APIs
- **Resilience** — Graceful degradation and offline capability
- **Auditability** — Every action is logged and tamper-evident

---

## Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SUPER ADMIN SERVER (Global)                         │
│                                                                              │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ Dashboard │  │ Institution│  │ Analytics│  │ Global Policy Engine     │  │
│  │ (React)   │  │ Manager    │  │ Engine   │  │                          │  │
│  └──────────┘  └────────────┘  └──────────┘  │ • Global RBAC Rules      │  │
│                                               │ • Compliance Checks      │  │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  │ • Audit Aggregation      │  │
│  │ License  │  │ Global     │  │ Update   │  │ • Threat Detection       │  │
│  │ Manager  │  │ Directory  │  │ Registry │  └──────────────────────────┘  │
│  └──────────┘  └────────────┘  └──────────┘                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        PostgreSQL (Global)                           │   │
│  │  institutions | licenses | global_policies | audit_log | updates    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │ TLS 1.3 / mTLS
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        INSTITUTION SERVER (Local)                           │
│                                                                              │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ Admin    │  │ User       │  │ Exam     │  │ Local Policy Engine      │  │
│  │ Portal   │  │ Directory  │  │ Manager  │  │                          │  │
│  └──────────┘  └────────────┘  └──────────┘  │ • Local RBAC Rules      │  │
│                                               │ • Network Zone Config   │  │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  │ • Exam Lockdown Policy  │  │
│  │ Device   │  │ Content    │  │ Reporting│  │ • Backup Schedule       │  │
│  │ Manager  │  │ Repository │  │ Engine   │  └──────────────────────────┘  │
│  └──────────┘  └────────────┘  └──────────┘                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL (Local) + Redis (Cache/Sessions)             │   │
│  │  users | devices | exams | results | courses | audit_log | config   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │ TLS 1.3 / WireGuard (VPN for exam traffic)
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       EDUOS CLIENT (Student/Faculty)                        │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │     User Space       │  │       Services       │  │    Security      │  │
│  │                      │  │                      │  │                  │  │
│  │ • KDE Plasma 6       │  │ • edos-daemon        │  │ • AppArmor      │  │
│  │ • Learn Hub (Web)    │  │ • edos-exam-daemon   │  │ • Auditd        │  │
│  │ • Exam Portal (Web)  │  │ • edos-update-daemon │  │ • Firewalld     │  │
│  │ • Cyber Lab (Docker) │  │ • edos-sync-daemon   │  │ • SELinux       │  │
│  │ • Dev Suite (IDEs)   │  │ • edos-admin-daemon  │  │ • FDE (LUKS)    │  │
│  │ • Admin Center (Web) │  │                      │  │                  │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     Debian 13 "Trixie" (Base)                       │   │
│  │  Linux Kernel 6.12 | systemd 256 | NetworkManager | PulseAudio    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Hardware Layer                                │   │
│  │  x86_64 | Secure Boot | TPM 2.0 | UEFI | 4GB+ RAM | 64GB+ Storage  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## System Boot Flow

The EduOS boot process ensures system integrity from power-on to login screen.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                            BOOT FLOW SEQUENCE                                 │
└────────────────────────────────────────────────────────────────────────────────┘

    Power On
       │
       ▼
┌──────────────────┐
│   UEFI Firmware   │  Secure Boot verifies bootloader signature
│   (BIOS Setup)    │  TPM 2.0 measures firmware state
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Shim/GRUB     │  GRUB verifies kernel + initrd against EduOS certificate
│   (Bootloader)   │  Passes encrypted cmdline parameters
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Linux Kernel   │  Kernel verifies signed modules before loading
│    (v6.12)       │  initramfs decrypts root FS (if FDE enabled)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│      systemd     │  PID 1 — starts target units
│    (init v256)   │
└────────┬─────────┘
         │
    ┌────┴──────────────┬──────────────────┐
    ▼                   ▼                  ▼
┌────────────┐  ┌──────────────┐  ┌──────────────┐
│ edos-daemon│  │ Network      │  │ Display      │
│ (security  │  │ Manager      │  │ Manager      │
│  policies) │  │ (connectivity)│  │ (SDDM)       │
└────────────┘  └──────────────┘  └──────────────┘
                                      │
    ┌─────────────────────────────────┴─────────────────────────┐
    │                                                           │
    ▼                                                           ▼
┌──────────────────┐                                  ┌──────────────────┐
│  SDDM Login      │                                  │  Auto-login      │
│  (Manual auth)   │                                  │  (managed labs)  │
└────────┬─────────┘                                  └────────┬─────────┘
         │                                                     │
         ▼                                                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        KDE Plasma 6 Desktop                         │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Startup Actions                           │   │
│  │  • edos-daemon starts (RBAC enforcement, audit, sync)       │   │
│  │  • edos-exam-daemon registers with Institution Server       │   │
│  │  • edos-update-daemon checks for updates                    │   │
│  │  • Learn Hub launches (Chromium kiosk)                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### Boot Failure Recovery

| Stage | Failure | Recovery |
|-------|---------|----------|
| UEFI | Bootloader signature invalid | Fallback to recovery partition |
| GRUB | Kernel signature mismatch | Boot previous kernel version |
| Kernel | Module load failure | Emergency shell |
| systemd | Service dependency failure | Automatic restart (3 attempts) |
| SDDM | Display manager crash | VT switch to fallback |

---

## Security Architecture

EduOS employs a defense-in-depth strategy across all layers.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       SECURITY ARCHITECTURE STACK                           │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER SECURITY                          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ Content Security │  │ Session          │  │ API Security             │  │
│  │ Policy (CSP)     │  │ Management       │  │ • OAuth 2.0 / OIDC       │  │
│  │ • Same-origin    │  │ • JWT with       │  │ • Rate limiting          │  │
│  │ • XSS protection │  │   rotating keys  │  │ • Request validation     │  │
│  │ • CSRF tokens    │  │ • 15-min expiry  │  │ • SQL injection          │  │
│  └──────────────────┘  │ • Secure cookies │  │   prevention             │  │
│                         └──────────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER SECURITY                              │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ RBAC Enforcement │  │ Audit Logging    │  │ Service Isolation        │  │
│  │                  │  │                  │  │                          │  │
│  │ • Policy         │  │ • Tamper-evident │  │ • systemd sandboxing     │  │
│  │   Decision Point │  │ • Remote logging │  │ • Private /tmp           │  │
│  │ • Policy         │  │ • Real-time      │  │ • Capability dropping    │  │
│  │   Administration │  │   alerts         │  │ • Network namespace      │  │
│  │ • Attribute      │  │ • Retention      │  │   isolation              │  │
│  │   Based Access   │  │   policies       │  │ • ReadOnly= / Protect*   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM LAYER SECURITY                               │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ Mandatory Access │  │ Network Security │  │ Filesystem Security      │  │
│  │ Control          │  │                  │  │                          │  │
│  │                  │  │ • firewalld      │  │ • Full Disk Encryption   │  │
│  │ • AppArmor       │  │ • nftables rules │  │   (LUKS + TPM)           │  │
│  │   profiles       │  │ • Exam network   │  │ • /usr read-only         │  │
│  │ • SELinux        │  │   isolation      │  │ • /etc immutable         │  │
│  │   policies       │  │ • WireGuard VPN  │  │ • tmpfs for /tmp         │  │
│  │ • Landlock LSM   │  │ • DNS over TLS   │  │ • dm-verity for system   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         HARDWARE LAYER SECURITY                             │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ Secure Boot (UEFI)   │  │ TPM 2.0          │  │ IOMMU / VT-d        │  │
│  │ • Verified chain     │  │ • Measured boot  │  │ • DMA protection    │  │
│  │ • Custom KEK          │  │ • Key storage    │  │ • Device isolation  │  │
│  │ • DBX revocation     │  │ • Remote         │  │ • PCIe ACS          │  │
│  └──────────────────────┘  │   attestation    │  └──────────────────────┘  │
│                            └──────────────────┘                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### RBAC Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ROLE HIERARCHY                                     │
│                                                                             │
│  super_admin ───────┬──────────────────────────────────────────────┐       │
│                     │                                              │       │
│              institution_admin                               global_viewer  │
│                     │                                              │       │
│          ┌──────────┼──────────┐                                   │       │
│          │          │          │                                   │       │
│    faculty_admin  it_admin  content_admin                           │       │
│          │          │          │                                   │       │
│       faculty ─────┼──────────┼───── viewer                       │       │
│                     │          │                                   │       │
│                 student ──────┘                                   │       │
│                                                                             │
│  Permissions:                                                                │
│  super_admin        — Full access across all institutions                  │
│  institution_admin  — Full access within one institution                   │
│  faculty_admin      — Manage courses, exams, grades                        │
│  it_admin           — Manage devices, network, updates                     │
│  content_admin      — Manage learning materials, curriculum                │
│  faculty            — Create exams, view analytics, manage classes         │
│  student            — Access Learn Hub, take exams, view grades            │
│  viewer             — Read-only access to dashboards                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Exam Data Flow

EduOS ensures end-to-end security for exam data from creation to result submission.

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                            EXAM DATA FLOW (SECURE END-TO-END)                              │
└────────────────────────────────────────────────────────────────────────────────────────────┘

                            EXAM CREATION PHASE
┌──────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   Faculty    │───────▶│   Web Interface   │───────▶│  Institution DB  │
│  (Browser)   │  TLS   │   (Admin Center)  │  TLS   │  (Encrypted)     │
└──────────────┘        └──────────────────┘        └──────────────────┘
                                                           │
                                                           │ AES-256-GCM
                                                           ▼
                                                  ┌──────────────────┐
                                                  │  Encrypted JSON  │
                                                  │  exam_manifest   │
                                                  │  {               │
                                                  │   "id": "uuid",  │
                                                  │   "title": "...", │
                                                  │   "questions":   │
                                                  │   [...encrypted] │
                                                  │  }               │
                                                  └──────────────────┘

                            EXAM DISTRIBUTION PHASE
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Institution DB   │───────▶│  Sync Service    │───────▶│  Client Device   │
│ (Encrypted at    │  mTLS  │  (edos-sync)     │  mTLS  │  (AES decrypted  │
│  rest)           │        │                  │        │   in memory)     │
└──────────────────┘        └──────────────────┘        └──────────────────┘

                            EXAM EXECUTION PHASE
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT DEVICE (LOCKDOWN MODE)                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Exam Portal (Chromium Kiosk)                  │   │
│  │  • Full-screen, no address bar, no dev tools                       │   │
│  │  • Clipboard disabled, print disabled, download disabled           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   edos-exam-daemon (systemd service)                │   │
│  │  • Monitors for policy violations (new processes, USB, etc.)       │   │
│  │  • Enforces network lockdown (allowlist only: exam server)         │   │
│  │  • Captures periodic screenshots for proctoring                    │   │
│  │  • Logs all system events during exam                              │   │
│  │  • Heartbeat to Institution Server (every 30s)                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Network State During Exam                    │   │
│  │  • Only allowed: exam server, institution server                   │   │
│  │  • Blocked: social media, messaging, file sharing, AI tools        │   │
│  │  • All traffic routed through exam proxy                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

                            EXAM SUBMISSION PHASE
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│  Client Device   │───────▶│  Institution     │───────▶│  Results Engine  │
│  (Signed +       │  mTLS  │  Server          │  TLS   │  (Decrypt,       │
│   Encrypted)     │        │  (Verify +       │        │   Grade, Store)  │
│                  │        │   Encrypt)       │        │                  │
│  {               │        └──────────────────┘        │  • Auto-grade    │
│   "exam_id":..., │                                    │    MCQs          │
│   "answers":     │                                    │  • Plagiarism    │
│   [...encrypted],│                                    │    check         │
│   "signature":   │                                    │  • Manual        │
│   "..."          │                                    │    review for    │
│  }               │                                    │    essays/code   │
└──────────────────┘                                    └──────────────────┘
```

---

## Update Flow

EduOS uses a signed, multi-stage update system with rollback capability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          UPDATE FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    UPDATE PUBLISHING (Super Admin)
┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────┐
│  Build       │──▶│  Sign with GPG   │──▶│  Upload to       │──▶│  Global  │
│  Pipeline    │   │  (EduOS Release  │   │  Update Registry │   │  Notify  │
│  (GitHub     │   │   Key)           │   │  (S3/CDN)        │   │  Inst.   │
│   Actions)   │   └──────────────────┘   └──────────────────┘   │  Servers │
└──────────────┘                                                └──────────┘
                                                                      │
                                                                      ▼
                    UPDATE DISTRIBUTION (Institution Server)
                                                    ┌──────────────────────┐
                               ┌───────────────────▶│  Cache & Verify     │
                               │                    │  • GPG signature    │
                               │                    │  • Checksum (SHA256)│
                               │                    │  • Dependency check │
                               │                    └──────────────────────┘
                               │                              │
                               │                              ▼
                               │                    ┌──────────────────────┐
                               │                    │  Stage Update       │
                               │                    │  • Download to cache│
                               │                    │  • Prepare A/B slots│
                               │                    └──────────────────────┘
                               │                              │
                               │                              ▼
                    UPDATE INSTALLATION (Client Device)
                               │                    ┌──────────────────────┐
                               └───────────────────▶│  edos-update-daemon │
                                                    │                      │
                                                    │  1. Download update  │
                                                    │  2. Verify signature │
                                                    │  3. Take snapshot    │
                                                    │     (for rollback)   │
                                                    │  4. Apply update     │
                                                    │  5. Reboot           │
                                                    │  6. Health check     │
                                                    │  7. Confirm success  │
                                                    └──────────────────────┘
                                                                      │
                              ┌───────────────────────────────────────┼───────────┐
                              │                                       │           │
                              ▼                                       ▼           ▼
                    ┌──────────────────┐                    ┌──────────────────┐
                    │  Success         │                    │  Failure         │
                    │  • Mark active   │                    │  • Auto-rollback │
                    │  • Report status │                    │  • Report error  │
                    │  • Cleanup old   │                    │  • Fall back to  │
                    │    snapshots     │                    │    known-good    │
                    └──────────────────┘                    └──────────────────┘
```

### Update Types

| Type | Scope | Frequency | Downtime |
|------|-------|-----------|----------|
| Security Patch | Packages | On-demand | Reboot required |
| System Update | Kernel + Base | Monthly | Reboot required |
| EduOS Feature | EduOS packages | Bi-weekly | Minimal (service restart) |
| Content Update | Courses/materials | Continuous | None |

---

## Network Topology

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                            NETWORK TOPOLOGY                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

                         INTERNET
                            │
                    ┌───────┴───────┐
                    │   Firewall    │  Perimeter firewall / IPS
                    │   (WAF/DDoS)  │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │   Load        │  HAProxy / nginx
                    │   Balancer    │  TLS termination
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────────┐
              │             │                   │
              ▼             ▼                   ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────────────┐
│  DMZ Network        │ │  Management Network │ │  Internal Network           │
│  /24                │ │  /24       │ │  /24              │
│                     │ │                     │ │                             │
│  • Web Server       │ │  • Admin Panel      │ │  • Client Devices (WiFi)    │
│  • API Gateway      │ │  • Monitoring       │ │  • Lab Computers (Ethernet) │
│  • Update Registry  │ │  • Backup Server    │ │  • Printers                 │
│  • VPN Endpoint     │ │  • Log Aggregator   │ │  • File Servers             │
└─────────────────────┘ └─────────────────────┘ └─────────────────────────────┘
                                                                     │
                                                          ┌──────────┴──────────┐
                                                          │                     │
                                                          ▼                     ▼
                                               ┌─────────────────────┐ ┌─────────────────────┐
                                               │  Student VLAN       │ │  Faculty VLAN       │
                                               │  /24    │ │  /24     │
                                               │                     │ │                     │
                                               │  • Network lockdown │ │  • Higher bandwidth │
                                               │    during exams     │ │  • Admin access      │
                                               │  • Content filtered │ │  • Content creation  │
                                               │  • Bandwidth limits │ │    privileges        │
                                               └─────────────────────┘ └─────────────────────┘
```

### Port Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| API Gateway | 443 | HTTPS | All API traffic |
| Institution DB | 5432 | PostgreSQL | Database access (internal only) |
| Redis | 6379 | TCP | Session/cache (internal only) |
| mTLS Sync | 8443 | HTTPS | Client-server sync |
| Exam WebSocket | 9443 | WSS | Real-time exam proctoring |
| WireGuard | 51820 | UDP | VPN for exam isolation |
| Update Registry | 443 | HTTPS | Package distribution |

---

## Database Schema

### Super Admin Database (Global)

```sql
-- Institutions
CREATE TABLE institutions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    domain          VARCHAR(255) UNIQUE NOT NULL,
    tier            VARCHAR(50) NOT NULL CHECK (tier IN ('basic', 'standard', 'enterprise')),
    max_devices     INT NOT NULL DEFAULT 100,
    max_users       INT NOT NULL DEFAULT 500,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Global Licenses
CREATE TABLE licenses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id  UUID REFERENCES institutions(id) ON DELETE CASCADE,
    license_key     VARCHAR(255) UNIQUE NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    seats_used      INT DEFAULT 0,
    seats_total     INT NOT NULL,
    is_active       BOOLEAN DEFAULT true
);

-- Global Policies
CREATE TABLE global_policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    policy_type     VARCHAR(50) NOT NULL,
    rules           JSONB NOT NULL,
    is_enforced     BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log (Global)
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ DEFAULT NOW(),
    source          VARCHAR(100) NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    actor_id        UUID,
    resource_type   VARCHAR(50),
    resource_id     UUID,
    action          VARCHAR(50) NOT NULL,
    details         JSONB,
    ip_address      INET,
    hash_chain      VARCHAR(64) NOT NULL  -- SHA256 of (prev_hash || event_data)
);
```

### Institution Database (Local)

```sql
-- Users
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(50) NOT NULL CHECK (role IN (
                        'super_admin', 'institution_admin', 'faculty_admin',
                        'it_admin', 'content_admin', 'faculty', 'student', 'viewer'
                    )),
    department      VARCHAR(255),
    is_active       BOOLEAN DEFAULT true,
    mfa_enabled     BOOLEAN DEFAULT false,
    password_changed_at TIMESTAMPTZ DEFAULT NOW(),
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Devices
CREATE TABLE devices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    hostname        VARCHAR(255) NOT NULL,
    mac_address     VARCHAR(17) UNIQUE NOT NULL,
    machine_id      VARCHAR(64) UNIQUE NOT NULL,
    os_version      VARCHAR(50) NOT NULL,
    kernel_version  VARCHAR(50),
    ip_address      INET,
    is_locked_down  BOOLEAN DEFAULT false,
    last_seen       TIMESTAMPTZ,
    enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT true
);

-- Courses
CREATE TABLE courses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) UNIQUE NOT NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    department      VARCHAR(255),
    created_by      UUID REFERENCES users(id),
    is_published    BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Enrollments
CREATE TABLE enrollments (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id       UUID REFERENCES courses(id) ON DELETE CASCADE,
    role            VARCHAR(50) CHECK (role IN ('student', 'faculty', 'ta')),
    enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, course_id)
);

-- Exams
CREATE TABLE exams (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id       UUID REFERENCES courses(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    exam_type       VARCHAR(50) NOT NULL CHECK (exam_type IN (
                        'mcq', 'coding', 'essay', 'mixed'
                    )),
    duration_minutes INT NOT NULL,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,
    total_points    INT NOT NULL,
    allow_retake    BOOLEAN DEFAULT false,
    lockdown_mode   BOOLEAN DEFAULT true,
    is_published    BOOLEAN DEFAULT false,
    created_by      UUID REFERENCES users(id),
    encrypted_payload BYTEA,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_time CHECK (end_time > start_time)
);

-- Exam Attempts
CREATE TABLE exam_attempts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id         UUID REFERENCES exams(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    start_time      TIMESTAMPTZ NOT NULL,
    submit_time     TIMESTAMPTZ,
    status          VARCHAR(50) CHECK (status IN (
                        'in_progress', 'submitted', 'timed_out',
                        'terminated', 'reviewed'
                    )),
    encrypted_answers BYTEA,
    score           DECIMAL(5,2),
    proctoring_log  JSONB,
    ip_address      INET,
    device_id       UUID REFERENCES devices(id)
);

-- Learning Materials
CREATE TABLE materials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id       UUID REFERENCES courses(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    type            VARCHAR(50) CHECK (type IN (
                        'document', 'video', 'quiz', 'assignment',
                        'interactive', 'external'
                    )),
    content_url     TEXT NOT NULL,
    order_index     INT DEFAULT 0,
    is_published    BOOLEAN DEFAULT false,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Exam Results
CREATE VIEW exam_results AS
SELECT
    e.id AS exam_id,
    e.title AS exam_title,
    c.code AS course_code,
    u.id AS student_id,
    u.full_name AS student_name,
    ea.start_time,
    ea.submit_time,
    (EXTRACT(EPOCH FROM (ea.submit_time - ea.start_time)) / 60)::INT
        AS duration_minutes,
    ea.score,
    CASE
        WHEN ea.score >= 90 THEN 'A'
        WHEN ea.score >= 80 THEN 'B'
        WHEN ea.score >= 70 THEN 'C'
        WHEN ea.score >= 60 THEN 'D'
        ELSE 'F'
    END AS grade
FROM exam_attempts ea
JOIN exams e ON ea.exam_id = e.id
JOIN courses c ON e.course_id = c.id
JOIN users u ON ea.user_id = u.id
WHERE ea.status = 'reviewed';
```

---

## Component Relationships

### Systemd Service Dependency Graph

```
                    ┌──────────────────┐
                    │  network.target  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────────┐
              │              │                   │
              ▼              ▼                   ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────────────┐
│  postgresql.service│ │  redis.service     │ │  edos-daemon.service       │
│  (database)        │ │  (cache/sessions)  │ │  (core daemon)             │
└────────┬───────────┘ └────────┬───────────┘ │                            │
         │                      │              │  • RBAC enforcement       │
         │                      │              │  • Policy engine         │
         │                      │              │  • Audit logging          │
         │                      │              │  • Device registration    │
         └──────────┬───────────┘              │  • Local sync             │
                    │                          └────────┬───────────────────┘
                    ▼                                   │
┌──────────────────────────────┐                        │
│  edos-admin.service          │                        │
│  (Admin API server)          │                        │
│                              │                        │
│  Requires: postgresql,       │                        │
│  edos-daemon                 │                        │
└──────────────────────────────┘                        │
                                                         │
                    ┌────────────────────────────────────┘
                    │              │              │
                    ▼              ▼              ▼
┌───────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│ edos-exam-daemon  │ │ edos-update-    │ │ edos-sync-daemon     │
│ (Exam lockdown)   │ │ daemon          │ │ (Institution sync)   │
│                   │ │ (Update mgmt)   │ │                      │
│ Requires:         │ │                 │ │ Requires:            │
│ edos-daemon,      │ │ Requires:       │ │ edos-daemon, network │
│ network-online    │ │ edos-daemon,    │ └──────────────────────┘
│                   │ │ network-online  │
└───────────────────┘ └─────────────────┘
```

### Package Dependencies

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      EDUOS PACKAGE DEPENDENCIES                              │
└──────────────────────────────────────────────────────────────────────────────┘

edos-core
  ├── edos-security
  │     ├── openssl (>= 3.2)
  │     ├── gnupg2
  │     └── apparmor-profiles
  ├── edos-daemon
  │     ├── python3 (>= 3.12)
  │     ├── python3-systemd
  │     ├── python3-psutil
  │     └── python3-aiohttp
  ├── edos-admin-service
  │     ├── python3-django
  │     ├── python3-djangorestframework
  │     ├── python3-psycopg2
  │     └── python3-redis
  ├── edos-exam-service
  │     ├── chromium (>= 120)
  │     ├── iptables
  │     └── wireguard-tools
  ├── edos-update-service
  │     ├── apt
  │     ├── dpkg
  │     └── python3-apt
  ├── edos-learn-hub
  │     ├── python3-django
  │     └── python3-jupyter
  ├── edos-cyber-lab
  │     ├── docker-ce
  │     ├── docker-compose
  │     └── python3-docker
  ├── edos-dev-suite
  │     ├── gcc (>= 13)
  │     ├── python3 (>= 3.12)
  │     ├── nodejs (>= 20)
  │     ├── openjdk-17-jdk
  │     ├── rustc
  │     └── git
  └── edos-ui-theme
        ├── plasma-desktop
        ├── plasma-workspace
        ├── sddm
        └── plymouth
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Debian 13 over Ubuntu | Stability, no Canonical dependencies, pure upstream |
| KDE Plasma 6 over GNOME | Lower resource usage, modern UI, better Wayland support |
| systemd services vs containers | Simpler architecture, native integration, lower overhead |
| PostgreSQL over MySQL | Better JSON support, audit capabilities, replication |
| JWT sessions over server sessions | Stateless, scalable, works across load-balanced deployments |
| GPG-signed updates over HTTPS-only | Offline verification, chain-of-trust, non-repudiation |
| WireGuard over OpenVPN | Modern, simple, in-kernel performance |
| mTLS for client-server | Mutual authentication, no passwords in transit |
| TPM-backed FDE over software | Hardware-backed security, measured boot |

---

*This architecture document is maintained by the EduOS core team. For questions, contact architecture@edos.edu.*
