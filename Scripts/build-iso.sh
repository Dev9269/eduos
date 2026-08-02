#!/bin/sh
# EduOS ISO Build — redirects to correct platform build
# For FreeBSD ISO: use GitHub Actions workflow build-freebsd-iso.yml
# For local QEMU test: see Documentation/BUILD.md

echo "EduOS ISO Build"
echo ""
echo "Primary build method (FreeBSD ISO):"
echo "  Push to GitHub → Actions → build-freebsd-iso workflow"
echo "  OR: gh workflow run build-freebsd-iso.yml"
echo ""
echo "For Debian ISO (legacy/dev only):"
echo "  See Packages/live-build/BUILD_PROCEDURE.md"
echo ""
echo "To test current build in QEMU:"
echo "  qemu-system-x86_64 -cdrom eduos-freebsd.iso -m 4096 -boot d"
