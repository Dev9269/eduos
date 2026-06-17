#!/bin/bash
# Install Docker on EduOS (post-install for ISO builds)
# Docker is excluded from the ISO due to requiring its own apt repo

set -e

if ! command -v docker &>/dev/null; then
    echo "Installing Docker Engine..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker student
    usermod -aG docker admin
    echo "Docker installed successfully."
    echo "Users must log out and back in to use docker without sudo."
else
    echo "Docker already installed."
fi
