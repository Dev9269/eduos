# EduOS Security Report

## Firewall Configuration
- **Status**: Active (UFW)
- **Default policy**: Deny incoming, Allow outgoing
- **Allowed ports**: 22/tcp (SSH, rate-limited), 5050/tcp (Learn Hub)
- **SSH rate limiting**: `ufw limit ssh/tcp` (6 connections per 30s)

## SSH Hardening
- `PermitRootLogin no` — Root SSH access disabled
- Password authentication available (key auth recommended)
- Only port 22 exposed

## Access Control
- **sudo**: Passwordless sudo configured for `jainam` only
- **student**: Standard user, no sudo access
- **exam**: Restricted shell (`/usr/local/bin/eduos-exam-shell`), no sudo
- **admin**: No sudo access (lab management via Admin Center app)
- Home directory permissions: 750 (owner rwx, group rx, others ---)
- Default umask: 027 (files created rw-r-----)

## Unnecessary Services Disabled
| Service | Status | Reason |
|---|---|---|
| apache2 | ✅ Disabled | No web server needed in base OS |
| bluetooth | ✅ Disabled | Not needed in lab environment |
| cups-browsed | ✅ Disabled | Network printer discovery |
| avahi-daemon | ✅ Disabled | mDNS not needed |
| ModemManager | ✅ Disabled | No modem hardware |
| postgresql | ✅ Disabled | Lazy-start on demand |
| redis-server | ✅ Disabled | Lazy-start on demand |

## Automatic Updates
- **unattended-upgrades**: Configured and active
- Update frequency: Daily package list, daily upgrades
- Autoclean: Weekly
- Only security updates installed automatically

## User Management
- Root account: Locked (no login)
- Guest account: Disabled
- Process accounting: Enabled (audit trails)
- Exam session: Full network isolation via iptables
- Exam session: Key event restrictions (Print Screen, Alt+Tab, Super, Escape)

## Remaining Recommendations
1. **Enable `fail2ban`** for additional SSH brute-force protection
2. **Configure `auditd`** for detailed security event logging
3. **Set up `rkhunter` / `chkrootkit`** for periodic rootkit scanning
4. **Enable AppArmor profiles** for Firefox and other network-facing apps
5. **Review cron jobs** for unauthorized entries periodically
