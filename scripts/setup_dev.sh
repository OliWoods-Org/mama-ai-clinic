#!/usr/bin/env bash
# Developer setup for MAMA AI Clinic.
# Run this on any macOS/Linux machine for local development.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

echo "=== MAMA AI Clinic -- Developer Setup ==="
echo "Project: ${PROJECT_DIR}"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is required. Install it and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python ${PYTHON_VERSION}"

# Create virtual environment
if [ ! -d "${PROJECT_DIR}/venv" ]; then
    echo "[>>] Creating virtual environment..."
    python3 -m venv "${PROJECT_DIR}/venv"
fi

# Activate and install dependencies
echo "[>>] Installing dependencies..."
source "${PROJECT_DIR}/venv/bin/activate"
pip install -q -r "${PROJECT_DIR}/app/requirements.txt"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start developing:"
echo "  source venv/bin/activate"
echo "  cd app && flask --app app:create_app run --host=0.0.0.0 --port=5000 --debug"
echo ""
echo "To download the model (requires internet, ~1.5GB):"
echo "  ./inference/download_model.sh"
echo ""
echo "To start llama-server (requires model downloaded + llama.cpp built):"
echo "  llama-server -m inference/models/gemma-4-e2b-Q4_K_M.gguf --host 127.0.0.1 --port 8081 -t 4 -c 2048"
