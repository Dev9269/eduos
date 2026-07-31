# EduOS v3.0 Testing Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Manual Testing Checklist](#manual-testing-checklist)
3. [Automated Testing with VirtualBox](#automated-testing-with-virtualbox)
4. [Performance Benchmarks](#performance-benchmarks)
5. [Security Testing](#security-testing)
6. [Exam Mode Testing](#exam-mode-testing)
7. [Network Testing](#network-testing)
8. [Hardware Compatibility](#hardware-compatibility)

---

## Overview

This guide describes the testing procedures for EduOS v3.0. Tests are organized into manual and automated categories, covering functionality, performance, security, and hardware compatibility.

### Test Environment Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Host OS** | Windows 10 / macOS 12 / Linux | Linux (Debian/Ubuntu) |
| **Virtualization** | VirtualBox 7.0+ | VirtualBox 7.0+ with Guest Additions |
| **Physical HW** | See Hardware Compatibility section | Multiple vendor configurations |
| **Network** | Isolated test network | Dedicated lab with PXE boot |

---

## Manual Testing Checklist

### Installation

- [ ] **ISO Boot**: Boot from ISO on UEFI and legacy BIOS systems
- [ ] **GRUB Menu**: Verify boot menu appears with correct branding
- [ ] **Plymouth Splash**: Animated boot splash displays correctly
- [ ] **SDDM Login**: Login screen appears with EduOS theme
- [ ] **Default Credentials**: Login with `edos`/`edos` succeeds
- [ ] **First Boot Wizard**: Setup wizard walks through all steps
- [ ] **Fresh Install**: Full installation to disk completes
- [ ] **Encrypted Install**: LUKS full-disk encryption works
- [ ] **Language Selection**: All supported languages display correctly
- [ ] **Keyboard Layout**: All layouts work as expected

### Desktop Environment

- [ ] **KDE Plasma 6**: Desktop loads without errors
- [ ] **EduOS Theme**: Custom theme applied (colors, widgets, icons)
- [ ] **Application Menu**: All EduOS applications listed
- [ ] **Desktop Icons**: Learn Hub, Exam Portal, Cyber Lab, Dev Suite, Admin Center present
- [ ] **System Tray**: Network, volume, battery, update icons functional
- [ ] **Virtual Desktops**: Switch between 4 desktops
- [ ] **Window Management**: Minimize, maximize, close, tile
- [ ] **Keyboard Shortcuts**: All shortcuts function (`Alt+F2`, `Meta+D`, etc.)
- [ ] **Wallpaper**: Default EduOS wallpaper displays
- [ ] **Panel Configuration**: Top and bottom panels render correctly

### Applications

- [ ] **Learn Hub**: Opens, displays dashboard, courses load
- [ ] **AI Tutor**: Chat interface works, responses appear
- [ ] **Exam Portal**: Opens, authentication works, exam list displays
- [ ] **Cyber Lab**: Launches, Docker scenarios start
- [ ] **Dev Suite**: VS Code, PyCharm, terminal open
- [ ] **Admin Center**: Opens, dashboard data displays
- [ ] **Update Manager**: Checks for updates, displays status

### System Services

- [ ] `edos-daemon` running (verify with `systemctl status`)
- [ ] `edos-exam-daemon` running
- [ ] `edos-update-daemon` running
- [ ] `edos-sync-daemon` running

---

## Automated Testing with VirtualBox

### Setup

```bash
# Install VirtualBox
sudo apt install virtualbox virtualbox-ext-pack

# Install test dependencies
pip install -r tests/requirements.txt
```

### Test Framework

EduOS uses `pytest` with custom VirtualBox integration:

```
tests/
├── conftest.py                   # Test configuration and fixtures
├── requirements.txt              # Test dependencies
├── pytest.ini                    # Pytest configuration
├── unit/
│   ├── test_security.py
│   ├── test_exam_engine.py
│   ├── test_update_service.py
│   └── test_config.py
├── integration/
│   ├── test_daemon_api.py
│   ├── test_admin_api.py
│   ├── test_exam_flow.py
│   └── test_sync_service.py
├── performance/
│   ├── test_boot_time.py
│   ├── test_memory_usage.py
│   └── test_concurrent_exams.py
└── security/
    ├── test_authentication.py
    ├── test_authorization.py
    ├── test_encryption.py
    └── test_network_isolation.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/security/

# Run with verbose output
pytest -v

# Run with code coverage
pytest --cov=edos --cov-report=html

# Run specific test
pytest tests/integration/test_exam_flow.py::test_exam_submission
```

### VirtualBox Test Automation

```python
# conftest.py
import pytest
import subprocess
import time

@pytest.fixture(scope="session")
def edos_vm():
    """Start an EduOS VM in VirtualBox for testing."""
    vm_name = "edos-test"

    # Create VM if not exists
    subprocess.run([
        "VBoxManage", "createvm",
        "--name", vm_name,
        "--ostype", "Debian_64",
        "--register"
    ])

    # Configure VM
    subprocess.run([
        "VBoxManage", "modifyvm", vm_name,
        "--memory", "4096",
        "--cpus", "4",
        "--nic1", "nat"
    ])

    # Attach ISO
    subprocess.run([
        "VBoxManage", "storageattach", vm_name,
        "--storagectl", "IDE",
        "--port", "0",
        "--device", "0",
        "--type", "dvddrive",
        "--medium", "build/EduOS-v3.0.iso"
    ])

    # Start VM
    subprocess.run(["VBoxManage", "startvm", vm_name, "--type", "headless"])
    time.sleep(30)  # Wait for boot

    yield vm_name

    # Cleanup
    subprocess.run(["VBoxManage", "controlvm", vm_name, "poweroff"])
    subprocess.run(["VBoxManage", "unregistervm", vm_name, "--delete"])
```

### Test Example

```python
# tests/integration/test_exam_flow.py
import pytest
import requests

def test_exam_submission(edos_vm):
    """Test complete exam flow: create, distribute, submit, grade."""
    admin_token = authenticate("admin", os.environ.get("EDUOS_ADMIN_PASSWORD"))

    # Create exam
    exam = create_exam(admin_token, {
        "title": "Test Exam",
        "course_id": "CS101",
        "duration": 30,
        "questions": [
            {
                "type": "mcq",
                "question": "What is 2+2?",
                "options": ["3", "4", "5"],
                "correct": "4",
                "points": 10
            }
        ]
    })

    # Distribute to student
    assign_exam(admin_token, exam["id"], student_id="student-1")

    # Student submits exam
    student_token = authenticate("student1", "password")
    submission = submit_exam(student_token, exam["id"], {
        "answers": [{"question_id": 1, "answer": "4"}]
    })

    # Verify grade
    assert submission["score"] == 10.0
    assert submission["status"] == "submitted"
```

---

## Performance Benchmarks

### Boot Time

```bash
# Measure boot time from GRUB to SDDM
sudo systemd-analyze

# Detailed boot analysis
sudo systemd-analyze blame

# Plot boot timeline
sudo systemd-analyze plot > boot.svg
```

| Metric | Target | Threshold |
|--------|--------|-----------|
| Total boot time | < 30s | < 45s |
| Kernel boot | < 5s | < 8s |
| Userspace init | < 25s | < 37s |
| SDDM readiness | < 30s | < 45s |
| Service startup | < 20s | < 30s |

### Memory Usage

```bash
# Measure idle memory usage
free -h

# Per-process memory
ps aux --sort=-%mem | head -20

# Memory benchmark script
python3 tests/performance/test_memory_usage.py
```

| Scenario | Target | Threshold |
|----------|--------|-----------|
| Idle desktop | < 1.5 GB | < 2.0 GB |
| Learn Hub open | < 2.0 GB | < 2.5 GB |
| Dev Suite (VS Code) | < 2.5 GB | < 3.0 GB |
| Cyber Lab (Docker) | < 3.0 GB | < 4.0 GB |
| Exam lockdown mode | < 1.8 GB | < 2.5 GB |

### CPU Utilization

```bash
# Monitor CPU during typical workloads
htop

# CPU benchmark
python3 tests/performance/test_cpu_usage.py
```

| Scenario | Target | Threshold |
|----------|--------|-----------|
| Idle | < 5% | < 10% |
| Web browsing | < 20% | < 30% |
| Code compilation | < 80% | < 95% |
| Exam proctoring | < 15% | < 25% |
| Multiple applications | < 50% | < 70% |

### Storage Performance

```bash
# Disk read/write benchmark
sudo hdparm -tT /dev/sda

# IOPS test
sudo fio --randrepeat=1 --ioengine=libaio --direct=1 \
         --name=test --bs=4k --size=1G --readwrite=randrw
```

| Metric | Target (SSD) | Target (HDD) |
|--------|-------------|-------------|
| Sequential read | > 500 MB/s | > 120 MB/s |
| Sequential write | > 400 MB/s | > 100 MB/s |
| Random read IOPS | > 50,000 | > 500 |
| Random write IOPS | > 30,000 | > 300 |

### Network Performance

```bash
# Bandwidth test
iperf3 -c institution.example.edu

# Latency test
ping -c 100 institution.example.edu
```

| Metric | Target | Threshold |
|--------|--------|-----------|
| Bandwidth (LAN) | > 900 Mbps | > 500 Mbps |
| Bandwidth (WAN) | > 50 Mbps | > 10 Mbps |
| Latency (LAN) | < 1 ms | < 5 ms |
| Latency (WAN) | < 20 ms | < 100 ms |
| Exam sync (1000 students) | < 30s | < 60s |

---

## Security Testing

### Authentication Tests

```bash
# Run authentication test suite
pytest tests/security/test_authentication.py -v
```

| Test | Expected Result |
|------|----------------|
| Valid credentials login | Success |
| Invalid password | Rejected |
| Brute force (10 attempts) | Account locked after 5 failed attempts |
| MFA with valid TOTP | Success |
| MFA with invalid TOTP | Rejected |
| Session token expiry | Token rejected after inactivity timeout |
| Session token tampering | Token rejected with invalid signature |
| LDAP authentication | Success with valid LDAP credentials |

### Authorization Tests

```bash
pytest tests/security/test_authorization.py -v
```

| Test | Expected Result |
|------|----------------|
| Student accesses own profile | Allowed |
| Student accesses other's profile | Denied (403) |
| Student creates exam | Denied (403) |
| Faculty creates exam | Allowed |
| Faculty deletes system config | Denied (403) |
| Admin manages all users | Allowed |
| API without token | Denied (401) |
| API with expired token | Denied (401) |
| RBAC policy change propagation | Effective within 30s |

### Encryption Tests

```bash
pytest tests/security/test_encryption.py -v
```

| Test | Expected Result |
|------|----------------|
| Exam data encryption at rest | AES-256-GCM, key not in plaintext |
| Exam data decryption | Correct plaintext with valid key |
| Tampered ciphertext | Decryption fails gracefully |
| TPM-backed key release | Key released only on valid PCR measurements |
| Full disk encryption | LUKS with LUKS2 header, Argon2 KDF |
| Secure Boot chain | All signatures verified |

### Penetration Testing

#### Network Scanning

```bash
# Scan for open ports (should be minimal)
nmap -sT -p- <edos-client-ip>

# Expected open ports:
# 443 (HTTPS - Institution Server)
# 8443 (mTLS - Sync service)
# 51820 (WireGuard - during exam)

# Scan for vulnerabilities
nmap --script vuln <edos-client-ip>
```

#### Web Application Testing

```bash
# Run OWASP ZAP against Admin Center
zap-cli quick-scan --self-contained \
    --spider http://<institution-server>/admin

# API fuzzing
python3 tests/security/api_fuzzer.py \
    --target http://localhost:8081 \
    --endpoints /api/v1/users,/api/v1/exams
```

| OWASP Category | Test | Expected |
|----------------|------|----------|
| Injection | SQLi, NoSQLi | All blocked |
| XSS | Reflected, Stored, DOM | All sanitized |
| CSRF | Cross-site request forgery | Tokens enforced |
| SSRF | Server-side request forgery | Internal network blocked |
| IDOR | Insecure direct object reference | UUIDs, permission check |
| Rate Limiting | API abuse | Throttled after threshold |

### Audit Log Tests

| Test | Expected Result |
|------|----------------|
| Login event logged | Timestamp, user, IP, result |
| Exam start logged | User, exam, device, timestamp |
| Permission denied logged | User, resource, action, timestamp |
| Admin action logged | Admin, action, resource, details |
| Log tampering | Hash chain detects modification |
| Log rotation | Old logs compressed, new logs writable |

---

## Exam Mode Testing

### Lockdown Mode

```bash
# Run exam lockdown tests
pytest tests/security/test_exam_lockdown.py -v
```

| Test | Expected Result |
|------|----------------|
| Exam Portal opens in fullscreen | No address bar, no window controls |
| Alt+F4 during exam | Blocked |
| Ctrl+Alt+Del during exam | Blocked or redirected |
| Opening terminal during exam | Blocked |
| Opening browser during exam | Blocked (except exam whitelist) |
| USB drive insertion during exam | Blocked |
| Printing during exam | Blocked |
| Screenshot during exam | Blocked (configurable) |
| Network access to social media | Blocked |
| Network access to exam server | Allowed |
| Copy/paste from exam content | Disabled |

### Network Isolation

```bash
# Verify exam network state
sudo firewall-cmd --get-active-zones
# Expected: edos-exam

# Verify allowed hosts
sudo firewall-cmd --zone=edos-exam --list-rich-rules
# Expected: only exam-server and institution-server

# Test connectivity
curl https://exam-server.example.edu  # Should succeed
curl https://youtube.com               # Should fail
```

### Proctoring

| Test | Expected Result |
|------|----------------|
| Screenshot capture | Image saved at configured interval |
| Webcam feed | Video stream available in proctor dashboard |
| Microphone feed | Audio stream available |
| Process monitoring | Suspicious processes logged and alerted |
| Network monitoring | Unusual traffic patterns detected |
| Face detection (optional) | Student present in frame |
| Multiple face detection | Alert raised |
| Heartbeat | Server receives regular heartbeat from client |

### Concurrent Exams

```bash
# Simulate concurrent exam load
python3 tests/performance/test_concurrent_exams.py \
    --students 100 \
    --duration 60 \
    --server https://institution-server.example.edu
```

| Metric | Target | Threshold |
|--------|--------|-----------|
| Max concurrent students | 500 | 1000 |
| Submission latency (p95) | < 2s | < 5s |
| Heartbeat processing | 10,000/min | 20,000/min |
| Proctoring stream bandwidth | < 5 Mbps per student | < 10 Mbps |
| Server CPU during peak | < 60% | < 80% |

---

## Network Testing

### Connectivity Tests

```bash
# Test basic connectivity
ping institution.example.edu
ping 8.8.8.8

# Test DNS resolution
nslookup institution.example.edu
nslookup edos.edu

# Test HTTPS connectivity
curl -I https://institution.example.edu/api/health

# Test mTLS connectivity
curl --cert client.crt --key client.key \
     https://institution.example.edu:8443/sync/health
```

### Network Profiles

| Profile | Test | Expected |
|---------|------|----------|
| Campus | 802.1X authentication | Connected |
| Home | DHCP, internet access | Connected |
| Exam | Lockdown, whitelist only | Restricted |
| VPN | WireGuard tunnel | Encrypted |
| Proxy | HTTP/HTTPS proxy | Traffic routed |

### Bandwidth Tests

```bash
# Download test
wget -O /dev/null https://speedtest.example.edu/testfile.bin

# iperf test
iperf3 -c institution-server.example.edu -t 30
```

### Failover Tests

| Scenario | Expected Behavior |
|----------|------------------|
| Network cable unplugged | Fall back to WiFi (if available) |
| WiFi disconnected | Show notification, attempt reconnection |
| Institution server unreachable | Cache data locally, sync when available |
| DNS failure | Fall back to configured alternate DNS |
| Proxy unavailable | Direct connection fallback |

---

## Hardware Compatibility

### Tested Configurations

| Vendor | Model | CPU | RAM | Storage | Status |
|--------|-------|-----|-----|---------|--------|
| **Dell** | Latitude 5430 | Intel i5-1245U | 8 GB | 256 GB SSD | Certified |
| **Dell** | OptiPlex 7080 | Intel i7-10700 | 16 GB | 512 GB SSD | Certified |
| **HP** | EliteBook 840 G9 | Intel i5-1235U | 8 GB | 256 GB SSD | Certified |
| **HP** | ProDesk 400 G7 | Intel i3-10100 | 8 GB | 256 GB SSD | Certified |
| **Lenovo** | ThinkPad T14 Gen 3 | AMD Ryzen 5 PRO 6650U | 16 GB | 512 GB SSD | Certified |
| **Lenovo** | ThinkCentre M75q | AMD Ryzen 3 5400U | 8 GB | 256 GB SSD | Certified |
| **ASUS** | ExpertBook B1 | Intel i5-1135G7 | 8 GB | 512 GB SSD | Compatible |
| **Acer** | TravelMate P4 | Intel i5-1240P | 8 GB | 256 GB SSD | Compatible |
| **Apple** | MacBook Pro (2019+) | Intel | 16 GB | 256 GB+ SSD | Experimental |

### Hardware Test Matrix

```bash
# Run hardware compatibility checks
bash tests/hardware/check-compatibility.sh
```

| Component | Test | Pass Criteria |
|-----------|------|---------------|
| **CPU** | All cores detected, frequency scaling | `lscpu` matches specs |
| **RAM** | Full capacity available | `free -h` matches installed |
| **Storage** | Drive detected, SMART health | `sudo smartctl -a /dev/sda` passes |
| **GPU** | Display output, acceleration | `glxinfo`, `glmark2` runs |
| **WiFi** | Connection, throughput | `iw dev wlan0 link` connected |
| **Ethernet** | Link detection, speed | `ethtool eth0` shows 1000baseT |
| **Bluetooth** | Device detection | `bluetoothctl list` shows adapter |
| **Audio** | Playback and recording | `speaker-test`, `arecord` |
| **Webcam** | Video capture | `ffplay /dev/video0` shows feed |
| **Touchpad** | Movement, clicks, gestures | `libinput list-devices` recognized |
| **Keyboard** | All keys register | `evtest` shows key events |
| **USB** | Device detection | `lsusb` shows devices |
| **TPM** | TPM 2.0 available | `systemd-cryptenroll --tpm2-device=list` |
| **Secure Boot** | Enabled and functional | `mokutil --sb-state` shows enabled |

### Testing Procedure for New Hardware

```bash
# 1. Boot EduOS on the target hardware
# 2. Run hardware detection
sudo edos-diag hardware

# 3. Run compatibility test suite
pytest tests/hardware/ -v

# 4. Generate compatibility report
sudo edos-diag hardware --report hardware-report.json

# 5. Submit report
# Upload to https://compatibility.edos.edu
```

---

## Continuous Integration

EduOS uses GitHub Actions for CI/CD:

```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y live-build debootstrap
          pip install -r tests/requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=edos
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Build packages
        run: bash scripts/build-packages.sh
```

---

## Reporting Defects

When reporting a test failure, include:

1. **Environment**: Hardware, VM or physical, EduOS version
2. **Test**: Test name and test file
3. **Expected**: What should happen
4. **Actual**: What actually happened
5. **Logs**: Relevant log output
6. **Screenshots**: Visual evidence if applicable

```bash
# Collect diagnostic information
sudo edos-diag export --output /tmp/edos-diag.tar.gz

# Attach to bug report
# https://github.com/edos/edos/issues/new
```

---

*Test thoroughly, ship confidently. — The EduOS QA Team*
