#!/bin/sh
# Install all EduOS service daemons on FreeBSD
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
RC_DIR="/usr/local/etc/rc.d"
for svc in eduos_exam_daemon eduos_sync_daemon \
           eduos_security_daemon eduos_update_daemon; do
    if [ -f "$SRC/$svc" ]; then
        cp "$SRC/$svc" "$RC_DIR/$svc"
        chmod +x "$RC_DIR/$svc"
        sysrc "${svc}_enable=YES" 2>/dev/null || true
        echo "Installed: $svc"
    fi
done
echo "All EduOS service daemons installed"
