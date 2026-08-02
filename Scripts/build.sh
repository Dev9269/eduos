#!/bin/sh
# EduOS Build Script v2.0 — FreeBSD and Linux compatible
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OS=$(uname -s)

echo "╔══════════════════════════════════════════╗"
echo "║     EduOS Build System v2.0          ║"
echo "╚══════════════════════════════════════════╝"
echo "OS: $OS | Project: $PROJECT_DIR"
echo ""

# Step 1: Run tests
echo "[1/4] Running test suite..."
cd "$PROJECT_DIR"
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -10
echo ""

# Step 2: Syntax check all Python files
echo "[2/4] Syntax checking Python files..."
ERRORS=0
find "$PROJECT_DIR" -name "*.py" -not -path "*/__pycache__/*" \
  -not -path "*/\.*" | while read -r pyfile; do
  if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
    echo "  SYNTAX ERROR: $pyfile"
    ERRORS=$((ERRORS + 1))
  fi
done
echo "  Python syntax check complete"
echo ""

# Step 3: Package EduOS files
echo "[3/4] Creating EduOS distribution package..."
DIST_DIR="$PROJECT_DIR/dist/eduos-$(date +%Y%m%d)"
mkdir -p "$DIST_DIR"

# Copy application modules
for module in AdminCenter ExamMode LearnHub DevSuite CyberLab \
              InstitutionManager EcosystemDashboard Server Services \
              Scripts Branding Themes design_system.py requirements.txt; do
  if [ -e "$PROJECT_DIR/$module" ]; then
    cp -r "$PROJECT_DIR/$module" "$DIST_DIR/"
  fi
done

echo "  Distribution package: $DIST_DIR"
echo ""

# Step 4: Trigger GitHub Actions ISO build (if on CI)
echo "[4/4] ISO build..."
if [ -n "$GITHUB_ACTIONS" ]; then
  echo "  Running on GitHub Actions — ISO build via build-freebsd-iso.yml"
else
  echo "  Local build: push to GitHub to trigger ISO build"
  echo "  Or run: gh workflow run build-freebsd-iso.yml"
fi

echo ""
echo "Build complete. Distribution: dist/"
