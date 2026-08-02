#!/bin/sh
# EduOS FreeBSD ISO boot test — boots the ISO in QEMU and verifies
# the eduos-server comes up and answers a health check.
#
# Usage:  bash Scripts/test-freebsd-iso.sh [path/to/eduos-freebsd.iso]
# Env:    EDUOS_QEMU_TIMEOUT  (seconds to wait for server, default 180)
#         EDUOS_QEMU_MEM      (MB, default 2048)
#         EDUOS_QEMU_HEADLESS (set to 1 to force -nographic)
set -e

ISO="${1:-eduos-freebsd.iso}"
TIMEOUT="${EDUOS_QEMU_TIMEOUT:-180}"
MEM="${EDUOS_QEMU_MEM:-2048}"
SSH_PORT=2222
API_PORT=8080
LOGFILE="$(mktemp /tmp/eduos-qemu.XXXXXX.log)"
PIDFILE="$(mktemp /tmp/eduos-qemu.XXXXXX.pid)"

cleanup() {
    if [ -f "$PIDFILE" ]; then
        kill "$(cat "$PIDFILE")" 2>/dev/null || true
        rm -f "$PIDFILE"
    fi
    rm -f "$LOGFILE"
}
trap cleanup EXIT INT TERM

if [ ! -f "$ISO" ]; then
    echo "ERROR: ISO not found: $ISO" >&2
    exit 1
fi

command -v qemu-system-x86_64 >/dev/null 2>&1 || command -v qemu-system-x86 >/dev/null 2>&1 || {
    echo "ERROR: qemu-system-x86_64 not installed" >&2
    exit 1
}

echo "[test-freebsd-iso] Booting $ISO in QEMU (mem=${MEM}MB, timeout=${TIMEOUT}s)"
qemu-system-x86_64 \
    -m "$MEM" \
    -cdrom "$ISO" \
    -boot d \
    -netdev user,id=net0,hostfwd=tcp::"$SSH_PORT"-:22,hostfwd=tcp::"$API_PORT"-:8000 \
    -device e1000,netdev=net0 \
    -display none -serial file:"$LOGFILE" \
    -no-reboot \
    >"$LOGFILE" 2>&1 &
echo "$!" > "$PIDFILE"

WAITED=0
SERVER_UP=0
while [ "$WAITED" -lt "$TIMEOUT" ]; do
    if curl -fsS "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; then
        SERVER_UP=1
        break
    fi
    if ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "ERROR: QEMU exited early (see log below)" >&2
        tail -n 40 "$LOGFILE" >&2
        exit 1
    fi
    sleep 5
    WAITED=$((WAITED + 5))
done

if [ "$SERVER_UP" -eq 1 ]; then
    BODY="$(curl -fsS "http://127.0.0.1:${API_PORT}/health")"
    echo "[test-freebsd-iso] PASS — eduos-server answered /health: $BODY"
    exit 0
fi

echo "ERROR: eduos-server did not answer /health within ${TIMEOUT}s" >&2
tail -n 60 "$LOGFILE" >&2
exit 1
