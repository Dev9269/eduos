#!/bin/sh
# Install EduOS agent on a FreeBSD student machine
# Run as root: sh Services/freebsd/install-agent-freebsd.sh

set -e

echo "Installing EduOS Agent for FreeBSD..."

# Install Python and dependencies
pkg install -y python311 py311-pip py311-websockets py311-psutil

# Install EduOS files
mkdir -p /opt/eduos/Services
cp Services/eduos-agent.py /opt/eduos/Services/

# Install rc.d service
cp Services/freebsd/eduos_agent /usr/local/etc/rc.d/
chmod +x /usr/local/etc/rc.d/eduos_agent

# Configure agent
mkdir -p /etc/eduos
if [ ! -f /etc/eduos/agent.conf ]; then
    echo '{"server_url": "ws://eduos-server.local:8765", "token": ""}' \
        > /etc/eduos/agent.conf
    chmod 600 /etc/eduos/agent.conf
fi

# Enable and start
sysrc eduos_agent_enable="YES"
service eduos_agent start

echo "EduOS Agent installed and started."
echo "Edit /etc/eduos/agent.conf to set the server IP."
