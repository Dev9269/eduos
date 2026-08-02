#!/bin/sh
# EduOS Settings launcher — runs the settings app from the packaged tree.
APP_DIR="/usr/lib/edos/apps/settings"
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="/opt/eduos/Packages/eduos-settings/usr/lib/edos/apps/settings"
fi
if [ ! -d "$APP_DIR" ]; then
    echo "EduOS Settings not found (looked in /usr/lib/edos and /opt/eduos)" >&2
    exit 1
fi
export PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m settings
