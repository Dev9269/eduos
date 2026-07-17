# EduOS v3.0 Administrator Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [User Management](#user-management)
4. [Device Management](#device-management)
5. [Security Configuration](#security-configuration)
6. [Exam Configuration](#exam-configuration)
7. [Updates and Maintenance](#updates-and-maintenance)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The EduOS Administrator Guide provides detailed instructions for configuring and maintaining EduOS within an educational institution. There are three administrative tiers:

| Role | Scope | Responsibilities |
|------|-------|------------------|
| **Super Admin** | All institutions | Global configuration, license management, system-wide policies |
| **Institution Admin** | Single institution | Full control over users, devices, exams, and settings |
| **Department Admin** | Department-level | Limited to department resources and users |

### Admin Center Access

- **URL**: `https://<institution-server>/admin`
- **Direct access**: Click the **Admin Center** icon on the desktop
- **Required**: Institution Admin or higher role

---

## Installation

### Fresh Installation

#### Method 1: ISO Installation (Recommended)

1. **Download the ISO**
   ```bash
   wget https://releases.edos.edu/EduOS-v3.0.iso
   wget https://releases.edos.edu/EduOS-v3.0.iso.sig
   gpg --verify EduOS-v3.0.iso.sig EduOS-v3.0.iso
   ```

2. **Create installation media**
   ```bash
   # USB drive (replace /dev/sdX with your device)
   dd if=EduOS-v3.0.iso of=/dev/sdX bs=4M status=progress conv=fsync
   ```

3. **Boot from USB**
   - Enter BIOS/UEFI setup (F2, F12, Del depending on hardware)
   - Disable Secure Boot temporarily (re-enable after installation)
   - Set USB as first boot device
   - Save and reboot

4. **Installation Steps**
   - Select **"Install EduOS v3.0"** from the GRUB menu
   - Choose your language and keyboard layout
   - Configure network (optional during install)
   - Partition disk:
     - Automatic: Guided — use entire disk with LUKS encryption
     - Manual: Custom partition layout
   - Create user account
   - Complete installation and reboot

#### Method 2: Network PXE Boot

For large-scale deployments across a computer lab:

1. Set up a PXE server on the institution network
2. Configure DHCP to point to the PXE server
3. Add the EduOS netboot image to the PXE server
4. Boot target machines via network (PXE option in BIOS)

### Post-Installation Setup

1. **Register device with Institution Server**
   ```bash
   sudo edos-register --server https://institution.example.edu
   ```

2. **Configure enrollment settings**
   ```bash
   sudo edos-admin enroll --config
   ```

3. **Verify installation**
   ```bash
   edos-verify-installation
   ```

### Upgrading from v2.x

EduOS v3.0 is a complete rebuild and does not support in-place upgrades from v2.x. A fresh installation is required. See the [Migration Guide](https://docs.edos.edu/migration/v2-to-v3) for data migration instructions.

---

## User Management

### Adding Users

#### Single User via Admin Center

1. Log in to the Admin Center
2. Navigate to **Users → Add User**
3. Fill in:
   - Username (auto-generated based on name)
   - Full name
   - Email address
   - Role (Student, Faculty, Faculty Admin, IT Admin)
   - Department
   - Course enrollments (optional)
4. Click **Create**
5. System generates a temporary password — provide this to the user

#### Bulk Import via CSV

1. Navigate to **Users → Import Users**
2. Prepare a CSV file with headers:
   ```csv
   username,full_name,email,role,department,courses
   jdoe,John Doe,jdoe@example.edu,student,Computer Science,CS101;CS102
   asmith,Alice Smith,asmith@example.edu,faculty,Mathematics,MATH201
   ```
3. Upload the CSV file
4. Review the parsed data
5. Click **Import**
6. Download the credentials file with generated passwords

#### LDAP/Active Directory Integration

1. Navigate to **Settings → Authentication → LDAP**
2. Configure:
   - Server URL: `ldaps://ldap.example.edu`
   - Base DN: `dc=example,dc=edu`
   - Bind DN: `cn=admin,dc=example,dc=edu`
   - User filter: `(objectClass=posixAccount)`
   - Group filter: `(objectClass=posixGroup)`
3. Map LDAP attributes to EduOS fields
4. Test connection
5. Enable synchronization (interval: 15/30/60 minutes)

### Managing Roles and Permissions

EduOS uses Role-Based Access Control (RBAC) with the following hierarchy:

```
super_admin
  └── institution_admin
        ├── faculty_admin
        ├── it_admin
        └── content_admin
              └── faculty
                    └── student
```

**To modify role permissions:**
1. Admin Center → **Security → Roles**
2. Select a role to edit
3. Modify permissions (check/uncheck)
4. Save changes

### Multi-Factor Authentication (MFA)

1. Navigate to **Settings → Security → MFA**
2. Choose enforcement level:
   - **Optional** — Users can enable MFA voluntarily
   - **Required for Faculty** — Faculty must use MFA
   - **Required for All** — All users must use MFA
3. Supported methods:
   - TOTP (Google Authenticator, Authy)
   - WebAuthn (hardware security keys)
   - Email OTP (fallback)

### Managing User Sessions

Admin Center → **Users → Active Sessions**

| Column | Description |
|--------|-------------|
| User | Username and full name |
| Device | Hostname and IP address |
| Login Time | When the session started |
| Last Activity | Most recent action |
| Status | Active / Idle / Locked |

**Actions**: View details, Send message, Force logout, Lock account

---

## Device Management

### Enrolling Devices

#### Automatic Enrollment (Student Self-Service)

1. Student boots EduOS on their device
2. Device contacts the Institution Server
3. Student enters their credentials
4. Device is enrolled and associated with the student

#### Manual Enrollment (Admin)

1. Admin Center → **Devices → Enroll Device**
2. Enter:
   - MAC address
   - Machine ID (from `sudo cat /var/lib/dbus/machine-id`)
   - Assigned user
   - Device group
3. Click **Enroll**

#### Pre-Enrollment (Bulk)

For computer labs:

1. Admin Center → **Devices → Pre-Enroll**
2. Upload a CSV:
   ```csv
   mac_address,hostname,assigned_user,device_group,lab_name
   AA:BB:CC:DD:EE:01,lab-pc-01,,student-lab,Lab A
   AA:BB:CC:DD:EE:02,lab-pc-02,,student-lab,Lab A
   ```
3. Devices are pre-registered — they auto-enroll on first boot

### Device Groups

Create groups to manage devices collectively:

| Group | Purpose |
|-------|---------|
| student-lab | Computer lab machines |
| faculty-laptops | Faculty-issued laptops |
| library-kiosks | Public access terminals |
| exam-terminals | Dedicated exam workstations |

**Group settings**: Update policy, software, and configuration at the group level.

### Device Policies

| Policy | Description |
|--------|-------------|
| Allow USB Storage | Enable/disable USB mass storage |
| Allow Bluetooth | Enable/disable Bluetooth |
| Allow Printing | Enable/disable printing |
| Allow External Boot | Allow/disallow booting from external media |
| Lockdown Schedule | Schedule automatic exam lockdown |
| Bandwidth Limit | Maximum network bandwidth per device |
| Screen Lock Timeout | Idle timeout before screen locks |
| Installation Lock | Prevent unauthorized software installation |

### Remote Commands

Admin Center → **Devices → [Device] → Remote**

| Command | Description |
|---------|-------------|
| Lock Screen | Immediately lock the device |
| Shutdown | Power off the device |
| Restart | Reboot the device |
| Send Message | Display a notification on the device |
| Wipe Device | Factory reset the device |
| Force Update | Trigger an immediate update check |
| Enter Exam Mode | Remotely initiate exam lockdown |

---

## Security Configuration

### Firewall Rules

EduOS uses `firewalld` with preconfigured zones.

```bash
# View current zones
sudo firewall-cmd --get-active-zones

# EduOS exam zone (restrictive)
sudo firewall-cmd --zone=edos-exam --add-source=192.168.1.0/24
sudo firewall-cmd --zone=edos-exam --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="443" protocol="tcp" accept'

# Allow only exam server
sudo firewall-cmd --zone=edos-exam --add-rich-rule='rule family="ipv4" destination address="10.0.0.10" accept'
sudo firewall-cmd --zone=edos-exam --set-target=DROP
```

### AppArmor Profiles

```bash
# List AppArmor profiles
sudo aa-status

# Enforce EduOS profiles
sudo aa-enforce /etc/apparmor.d/usr.sbin.edos-daemon
sudo aa-enforce /etc/apparmor.d/usr.sbin.edos-exam-daemon

# Check for AppArmor denials
sudo journalctl -t audit --grep="apparmor"
```

### Audit Logging

EduOS uses `auditd` with custom rules:

```bash
# View audit rules
sudo auditctl -l

# Search audit log for login events
sudo ausearch --message USER_LOGIN --success yes

# Generate audit report
sudo aureport --login --summary

# Real-time monitoring
sudo tail -f /var/log/audit/audit.log
```

### Intrusion Detection

EduOS integrates with AIDE (Advanced Intrusion Detection Environment):

```bash
# Initialize database
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run integrity check
sudo aide --check

# Update database after software changes
sudo aide --update
```

---

## Exam Configuration

### Creating an Exam

1. Admin Center → **Exams → Create Exam**
2. Configure settings:

| Setting | Description |
|---------|-------------|
| **Title** | Exam name displayed to students |
| **Course** | Associated course |
| **Exam Type** | MCQ, Coding, Essay, Mixed |
| **Duration** | Time limit in minutes |
| **Schedule** | Start and end date/time |
| **Max Attempts** | Number of allowed attempts |
| **Lockdown Mode** | Enable/disable exam lockdown |
| **Network Whitelist** | Allowed URLs during exam (lockdown) |
| **Proctoring** | Enable live proctoring, recording, or none |

3. Add questions via:
   - **Question Builder** — Create questions individually
   - **Import** — Import from CSV, QTI, or previous exams
   - **Question Bank** — Reuse questions from a shared pool

4. Configure grading:
   - Auto-grade for MCQs
   - Rubric-based for essays
   - Test-case-based for coding questions

5. Publish the exam

### Question Types

| Type | Description | Auto-Grade |
|------|-------------|------------|
| Multiple Choice (Single) | One correct answer | Yes |
| Multiple Choice (Multi) | Multiple correct answers | Yes |
| True/False | Binary choice | Yes |
| Fill in the Blank | Text input | Yes (exact match) |
| Short Answer | Brief written response | Manual |
| Essay | Extended written response | Manual (rubric) |
| Code | Write and run code | Test cases |
| File Upload | Submit a file | Manual |
| Matching | Pair items | Yes |
| Ordering | Arrange items | Yes |
| Drag and Drop | Visual arrangement | Yes |

### Exam Lockdown Configuration

```bash
# Custom lockdown policy file
/etc/edos/exam-lockdown.conf
```

```ini
[network]
allowed_hosts = exam-server.example.edu, institution.example.edu
block_all_others = true
dns_over_https = true

[processes]
blocked_processes = chrome, firefox, telegram, discord, slack
allowed_processes = edos-exam-daemon, chromium-exam, xdg-desktop

[devices]
block_usb_storage = true
block_bluetooth = true
block_printing = true
block_screenshots = false

[monitoring]
heartbeat_interval = 30
screenshot_interval = 60
enable_webcam = false
enable_microphone = false
log_process_events = true
```

### Proctoring Options

| Mode | Description | Storage |
|------|-------------|---------|
| **None** | No proctoring, trust-based | — |
| **Recording** | Record screen and audio during exam | Encrypted, local, uploaded after exam |
| **Live** | Real-time monitoring by proctor | Streamed to proctor dashboard |
| **Automated** | AI-based anomaly detection | Analyzed post-exam |

### Exam Results and Grading

1. Admin Center → **Exams → [Exam] → Results**
2. View aggregate statistics:
   - Score distribution
   - Average, median, high, low scores
   - Per-question analysis (difficulty, discrimination)
3. Manual grading:
   - Click **Grade** on an attempt
   - Review essay/code answers
   - Apply rubric
   - Add comments
   - Save grade
4. Release grades to students

---

## Updates and Maintenance

### Update Channels

| Channel | Description | Stability | Frequency |
|---------|-------------|-----------|-----------|
| **Stable** | Production-ready | Highest | Monthly |
| **Security** | Critical security patches | High | As needed |
| **Beta** | Pre-release features | Medium | Bi-weekly |
| **Alpha** | Development builds | Low | Weekly |

To set the update channel:

```bash
sudo edos-update set-channel stable
```

### Managing Updates

#### Check for Updates

```bash
# Via CLI
sudo edos-update check

# Via Admin Center
Updates → Check Now
```

#### Install Updates

```bash
# Apply available updates
sudo edos-update apply

# Apply with reboot
sudo edos-update apply --reboot

# Schedule update for maintenance window
sudo edos-update schedule --time "2026-07-15 02:00"
```

#### Rollback

```bash
# List available snapshots
sudo edos-update snapshots

# Rollback to a specific snapshot
sudo edos-update rollback --snapshot 20260701

# Rollback to previous state
sudo edos-update rollback --previous
```

### Scheduled Maintenance Windows

Admin Center → **Settings → Maintenance**

| Setting | Description |
|---------|-------------|
| Window Start | Time when maintenance can begin |
| Window End | Deadline for maintenance completion |
| Apply Security Updates | Install security patches immediately |
| Require Restart | Whether a reboot is needed |
| Notify Users | Send notification before maintenance |
| Maximum Downtime | Acceptable downtime per month |

### System Monitoring

#### Dashboard Metrics

Admin Center → **Monitoring**

| Metric | Description |
|--------|-------------|
| Active Users | Currently logged-in users |
| Online Devices | Devices currently connected |
| Exam Activity | Ongoing and upcoming exams |
| Storage Usage | Institution server disk usage |
| Update Status | Number of devices up-to-date |
| Security Alerts | Recent security events |

#### CLI Monitoring

```bash
# Service status
sudo systemctl status edos-daemon
sudo systemctl status edos-admin-service

# Resource usage
edos-monitor --dashboard

# Export metrics
edos-monitor --export --format json
```

---

## Backup and Recovery

### Backup Types

| Type | Content | Frequency | Retention |
|------|---------|-----------|-----------|
| **Full** | Complete system + data | Weekly | 4 weeks |
| **Incremental** | Changes since last backup | Daily | 2 weeks |
| **Configuration** | System settings only | On change | 3 months |
| **Exam Data** | Exams and results | After each exam | 1 year |

### Performing Backups

#### Via CLI

```bash
# Full backup
sudo edos-backup create --type full

# Incremental backup
sudo edos-backup create --type incremental

# Configuration backup only
sudo edos-backup create --type config

# Backup to remote location
sudo edos-backup create --remote s3://backups/edos/
```

#### Via Admin Center

1. Navigate to **Maintenance → Backup**
2. Click **Create Backup**
3. Select backup type
4. Configure options (encryption, compression, destination)
5. Click **Start**

### Recovery

#### Restore from Backup

```bash
# List available backups
sudo edos-backup list

# Restore latest backup
sudo edos-backup restore --latest

# Restore specific backup
sudo edos-backup restore --backup-id 20260701-120000

# Verify backup integrity
sudo edos-backup verify --backup-id 20260701-120000
```

#### Disaster Recovery

In the event of a complete system failure:

1. Perform a fresh installation of EduOS
2. Restore the Institution Server from backup:
   ```bash
   sudo edos-backup restore --from-medium /mnt/backup --type full
   ```
3. Re-register clients:
   ```bash
   sudo edos-admin devices resync
   ```
4. Verify exam data integrity:
   ```bash
   sudo edos-admin exams verify
   ```

---

## Troubleshooting

### Common Issues

#### Device Not Connecting to Institution Server

```bash
# Check network connectivity
ping institution.example.edu

# Verify DNS resolution
nslookup institution.example.edu

# Check service status
sudo systemctl status edos-daemon

# View logs
sudo journalctl -u edos-daemon --since "5 min ago"

# Re-register device
sudo edos-register --force
```

#### Exam Not Starting

```bash
# Check exam daemon status
sudo systemctl status edos-exam-daemon

# Verify exam schedule
sudo edos-admin exams list --upcoming

# Check network lockdown
sudo firewall-cmd --get-active-zones

# View exam logs
sudo journalctl -u edos-exam-daemon
```

#### User Cannot Log In

1. Verify the user account is active:
   ```bash
   sudo edos-admin users show <username>
   ```
2. Check authentication logs:
   ```bash
   sudo journalctl -u sddm
   sudo ausearch --message USER_LOGIN --success no
   ```
3. Reset password if needed:
   ```bash
   sudo edos-admin users reset-password <username>
   ```
4. Check account lockout status:
   ```bash
   sudo edos-admin users unlock <username>
   ```

#### Update Failing

```bash
# Check update service
sudo systemctl status edos-update-daemon

# View update logs
sudo journalctl -u edos-update-daemon --since "1 hour ago"

# Check disk space
df -h

# Verify update signature
sudo edos-update verify

# Force re-download
sudo edos-update check --force
```

### Logs Reference

| Log Location | Service | Contents |
|-------------|---------|----------|
| `journalctl -u edos-daemon` | Core daemon | General system events |
| `journalctl -u edos-admin-service` | Admin API | Admin actions |
| `journalctl -u edos-exam-daemon` | Exam service | Exam events |
| `journalctl -u edos-update-daemon` | Update service | Update activity |
| `journalctl -u edos-sync-daemon` | Sync service | Data synchronization |
| `/var/log/audit/audit.log` | Auditd | Security events |
| `/var/log/edos/` | All services | Rotating log files |

### Diagnostic Commands

```bash
# System health check
edos-diag

# Network diagnostics
edos-diag network

# Security audit
edos-diag security

# Performance check
edos-diag performance

# Exam readiness check
edos-diag exam

# Export diagnostics for support
edos-diag export --output /tmp/edos-diag.tar.gz
```

### Getting Support

| Resource | Contact |
|----------|---------|
| **Institution IT Desk** | Local support |
| **EduOS Support Portal** | https://support.edos.edu |
| **Email** | support@edos.edu |
| **Emergency** | emergency@edos.edu (24/7 critical issues) |

---

*For additional assistance, refer to the full documentation at https://docs.edos.edu or contact your EduOS account manager.*
