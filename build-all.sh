#!/usr/bin/env bash
# =============================================================================
# build-all.sh — Full build pipeline for the Train Control app
#
# Run this script from the repository root:
#   chmod +x build-all.sh   (first time only, to make it executable)
#   ./build-all.sh
#
# What it does:
#   1. Freezes rest_server.py into a standalone binary with PyInstaller
#   2. Copies the binary into the packaging/ staging directory
#   3. Builds the Java modules with Maven
#   4. Creates a trimmed JRE with jlink
#   5. Creates a native installer with jpackage
#
# Prerequisites:
#   - Python 3.11+ with pip
#   - PyInstaller: pip install pyinstaller
#   - Java 21 JDK (must include jpackage — Temurin / Oracle JDK 21 both do)
#   - Maven 3.8+
#   - macOS:   Xcode Command Line Tools (for .dmg packaging)
#   - Windows: WiX Toolset 3.x (for .msi packaging) — install via:
#                choco install wixtoolset
#   - Linux:   fakeroot + dpkg  — install via:
#                sudo apt-get install fakeroot dpkg
# =============================================================================

set -euo pipefail  # exit immediately on any error; treat unset vars as errors

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPTS_DIR="$SCRIPT_DIR/backend/src/main/PythonScripts"
PACKAGING_DIR="$SCRIPT_DIR/packaging"

echo "============================================"
echo "  Train Control — Full Build Pipeline"
echo "============================================"
echo ""

# --------------------------------------------------------------------------
# STEP 1 — Install Python dependencies and freeze rest_server.py
# --------------------------------------------------------------------------
echo "[1/5] Freezing rest_server.py with PyInstaller..."
cd "$PYTHON_SCRIPTS_DIR"

# Install pinned dependencies from requirements.txt into the current Python env.
# If you're using a virtualenv, activate it before running this script.
pip install -r requirements.txt --quiet

# Run PyInstaller using our spec file.
# Output goes to: backend/src/main/PythonScripts/dist/rest_server/
pyinstaller rest_server.spec --noconfirm

echo "      PyInstaller done."
echo ""

# --------------------------------------------------------------------------
# STEP 2 — Copy the PyInstaller output into the packaging/ staging directory
# --------------------------------------------------------------------------
echo "[2/5] Copying frozen server to packaging/ staging directory..."
cd "$SCRIPT_DIR"

rm -f "$PACKAGING_DIR/rest_server" "$PACKAGING_DIR/rest_server.exe"
cp "$PYTHON_SCRIPTS_DIR/dist/rest_server" "$PACKAGING_DIR/rest_server"
chmod +x "$PACKAGING_DIR/rest_server"

echo "      Staging directory ready: packaging/rest_server"
echo ""

# --------------------------------------------------------------------------
# STEP 3 — Build the Java modules with Maven
# --------------------------------------------------------------------------
echo "[3/5] Building Java modules with Maven..."
cd "$SCRIPT_DIR"

# -DskipTests speeds up the packaging build.
# Remove that flag if you want tests to run as part of the release build.
mvn clean package -DskipTests -pl backend,frontend --quiet

echo "      Maven build done."
echo ""

# --------------------------------------------------------------------------
# STEP 4 — Create a trimmed JRE with jlink
# --------------------------------------------------------------------------
echo "[4/5] Creating trimmed JRE with jlink..."
cd "$SCRIPT_DIR"

# This calls the jlink exec defined in frontend/pom.xml.
# The resulting JRE lands in: frontend/target/runtime/
mvn exec:exec@jlink -pl frontend --quiet

echo "      jlink done. Trimmed JRE at: frontend/target/runtime/"
echo ""

# --------------------------------------------------------------------------
# STEP 5 — Create the native installer with jpackage
# --------------------------------------------------------------------------
echo "[5/5] Creating native installer with jpackage..."
cd "$SCRIPT_DIR"

# This calls the jpackage exec defined in frontend/pom.xml.
# The installer lands in: frontend/target/installer/
#   macOS:   TrainControl-1.0.0.dmg
#   Windows: TrainControl-1.0.0.msi
#   Linux:   traincontrol_1.0.0-1_amd64.deb
mvn exec:exec@jpackage -pl frontend --quiet

echo "      jpackage done."
echo ""
echo "============================================"
echo "  BUILD COMPLETE"
echo "  Installer: frontend/target/installer/"
echo "============================================"

