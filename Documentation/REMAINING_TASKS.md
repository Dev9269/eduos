# EduOS Remaining Tasks

## High Priority

### 1. Kernel Disk Expansion
- **Issue**: 64 GiB unpartitioned space on /dev/sda; root partition only 18.9 GiB (90% full)
- **Fix**: Expand sda1 using growpart + resize2fs
- **Blocks**: ISO build (needs 5-8 GB free)
- **Risk**: Medium — requires unmounting or live boot for safe expansion

### 2. OBS Studio, Kdenlive, Krita
- **Issue**: Media creation tools not installed (require ~1-2 GB)
- **Fix**: Install when disk space permits
- **Priority**: Medium — useful for multimedia courses

### 3. Desktop Beginner Mode
- **Issue**: No simplified application menu for new users
- **Fix**: Create an EduOS Beginner desktop profile with reduced options
- **Priority**: Medium — improves student experience

## Medium Priority

### 4. R, Octave, GNUplot, GeoGebra
- **Scientific stack**: Useful for engineering/math courses
- **Install**: `sudo apt install r-base octave gnuplot geogebra`
- **Size**: ~500MB total

### 5. Admin Center SSH Remote Execution
- **Issue**: Lab management UI exists but no actual remote command execution
- **Fix**: Implement paramiko-based SSH command execution
- **Complexity**: Medium — requires SSH key distribution

### 6. Automated Update Distribution
- **Issue**: UI exists but no mechanism to push updates to lab machines
- **Fix**: Create rsync/APT-mirror based distribution pipeline

## Low Priority

### 7. Scribus (Desktop Publishing)
- **Install**: `sudo apt install scribus`
- **Size**: ~50MB

### 8. Metasploit, exploitdb
- **Note**: Not available in Debian repos; install from git if needed
- **metasploit**: `git clone https://github.com/rapid7/metasploit-framework`
- **exploitdb**: `git clone https://gitlab.com/exploit-database/exploitdb`

## Items Intentionally Deferred

| Feature | Phase | Notes |
|---|---|---|
| Exam Mode full development | Next phase | Complete, ready for next phase |
| Admin Center full development | Next phase | Complete, ready for next phase |
| Learn Hub full development | Next phase | Already implemented per previous phase |
| ISO generation | After Phase 2 | Blocked by disk space |
| Release engineering | After Phase 2 | Not yet started |
| LDAP/SSO integration | Phase 4 | Centralized authentication |
| LMS sync adapter | Phase 4 | Moodle API integration |
| Pre-configured course templates | Future | DevSuite enhancement |
