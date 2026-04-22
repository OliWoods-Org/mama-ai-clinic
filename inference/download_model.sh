#!/usr/bin/env bash
# Download the default model GGUF for Pi AI Clinic
# Run this during image build or on a machine with internet access.
# The Pi itself runs fully offline after this.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="${SCRIPT_DIR}/models"

# Default model: Gemma 4 E2B Q4_K_M
MODEL_REPO="google/gemma-4-e2b-gguf"
MODEL_FILE="gemma-4-e2b-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"

# Fallback model: Gemma 3 1B Q4_K_M
FALLBACK_REPO="google/gemma-3-1b-it-gguf"
FALLBACK_FILE="gemma-3-1b-it-Q4_K_M.gguf"
FALLBACK_URL="https://huggingface.co/${FALLBACK_REPO}/resolve/main/${FALLBACK_FILE}"

echo "=== Pi AI Clinic Model Downloader ==="
echo ""

mkdir -p "${MODELS_DIR}"

download_model() {
    local url="$1"
    local dest="$2"
    local name="$3"

    if [ -f "${dest}" ]; then
        echo "[OK] ${name} already exists at ${dest}"
        return 0
    fi

    echo "[>>] Downloading ${name}..."
    echo "     From: ${url}"
    echo "     To:   ${dest}"
    echo ""

    if command -v wget &>/dev/null; then
        wget --show-progress -O "${dest}" "${url}"
    elif command -v curl &>/dev/null; then
        curl -L --progress-bar -o "${dest}" "${url}"
    else
        echo "[ERROR] Neither wget nor curl found. Install one and retry."
        exit 1
    fi

    echo "[OK] ${name} downloaded successfully."
}

echo "Downloading default model (Gemma 4 E2B Q4_K_M, ~1.5GB)..."
download_model "${MODEL_URL}" "${MODELS_DIR}/${MODEL_FILE}" "Gemma 4 E2B"

echo ""
read -rp "Also download fallback model (Gemma 3 1B, ~700MB)? [y/N] " response
if [[ "${response}" =~ ^[Yy]$ ]]; then
    download_model "${FALLBACK_URL}" "${MODELS_DIR}/${FALLBACK_FILE}" "Gemma 3 1B"
fi

echo ""
echo "=== Done. Models stored in ${MODELS_DIR} ==="
echo "To verify: ls -lh ${MODELS_DIR}/"
