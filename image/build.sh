#!/usr/bin/env bash
# Build a complete SD card image for MAMA AI Clinic.
# Produces a .img file ready to flash to a microSD card.
#
# Prerequisites:
#   - Docker (for reproducible ARM cross-compilation)
#   - ~10GB free disk space
#   - Internet access (downloads Pi OS base + model)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
BUILD_DIR="${PROJECT_DIR}/build"
OUTPUT_DIR="${PROJECT_DIR}/output"

IMAGE_NAME="mama-ai-clinic"
IMAGE_VERSION=$(date +%Y%m%d)

echo "=== MAMA AI Clinic -- SD Card Image Builder ==="
echo "Version: ${IMAGE_VERSION}"
echo "Build dir: ${BUILD_DIR}"
echo ""

mkdir -p "${BUILD_DIR}" "${OUTPUT_DIR}"

# Step 1: Download Raspberry Pi OS Lite (64-bit)
echo "[1/6] Downloading Raspberry Pi OS Lite base image..."
PI_OS_URL="https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-11-19/2024-11-19-raspios-bookworm-arm64-lite.img.xz"
PI_OS_FILE="${BUILD_DIR}/raspios-lite-arm64.img.xz"
PI_OS_IMG="${BUILD_DIR}/raspios-lite-arm64.img"

if [ ! -f "${PI_OS_IMG}" ]; then
    if [ ! -f "${PI_OS_FILE}" ]; then
        wget -q --show-progress -O "${PI_OS_FILE}" "${PI_OS_URL}"
    fi
    echo "Extracting..."
    xz -dk "${PI_OS_FILE}"
fi

# Step 2: Download the model
echo "[2/6] Ensuring model is available..."
bash "${PROJECT_DIR}/inference/download_model.sh" <<< "n"  # Skip fallback model

# Step 3: Build llama.cpp for aarch64
echo "[3/6] Cross-compiling llama.cpp for aarch64..."
LLAMA_BUILD="${BUILD_DIR}/llama-cpp-aarch64"
if [ ! -f "${LLAMA_BUILD}/llama-server" ]; then
    mkdir -p "${LLAMA_BUILD}"
    # Use Docker for cross-compilation
    docker run --rm \
        -v "${LLAMA_BUILD}:/output" \
        --platform linux/arm64 \
        debian:bookworm-slim bash -c '
            apt-get update -qq && apt-get install -y -qq git cmake g++ &&
            git clone --depth 1 https://github.com/ggml-org/llama.cpp /build &&
            cd /build && mkdir build && cd build &&
            cmake .. -DCMAKE_BUILD_TYPE=Release &&
            cmake --build . --config Release -j$(nproc) --target llama-server &&
            cp bin/llama-server /output/
        '
fi

# Step 4: Customize the image
echo "[4/6] Customizing image..."
CUSTOM_IMG="${BUILD_DIR}/${IMAGE_NAME}-${IMAGE_VERSION}.img"
cp "${PI_OS_IMG}" "${CUSTOM_IMG}"

# Mount and customize (requires sudo for loop device)
echo "This step requires sudo to mount the image..."
LOOP_DEV=$(sudo losetup -fP --show "${CUSTOM_IMG}")
MOUNT_DIR="${BUILD_DIR}/mnt"
mkdir -p "${MOUNT_DIR}"

# Mount the root partition (partition 2)
sudo mount "${LOOP_DEV}p2" "${MOUNT_DIR}"
sudo mount "${LOOP_DEV}p1" "${MOUNT_DIR}/boot/firmware"

# Copy application files
echo "[5/6] Installing MAMA AI Clinic into image..."
sudo mkdir -p "${MOUNT_DIR}/opt/pi-ai-clinic"
sudo cp -r "${PROJECT_DIR}/app" "${MOUNT_DIR}/opt/pi-ai-clinic/"
sudo cp -r "${PROJECT_DIR}/inference/config.yaml" "${MOUNT_DIR}/opt/pi-ai-clinic/"
sudo mkdir -p "${MOUNT_DIR}/opt/pi-ai-clinic/models"
sudo cp "${PROJECT_DIR}/inference/models/"*.gguf "${MOUNT_DIR}/opt/pi-ai-clinic/models/" 2>/dev/null || true
sudo cp "${LLAMA_BUILD}/llama-server" "${MOUNT_DIR}/usr/local/bin/"

# Install systemd services
sudo tee "${MOUNT_DIR}/etc/systemd/system/llama-server.service" > /dev/null <<'EOF'
[Unit]
Description=MAMA AI Clinic - LLM Inference Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/llama-server \
    -m /opt/pi-ai-clinic/models/gemma-4-e2b-Q4_K_M.gguf \
    --host 127.0.0.1 --port 8081 \
    -t 4 -c 2048 --batch-size 512
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo tee "${MOUNT_DIR}/etc/systemd/system/pi-ai-clinic.service" > /dev/null <<'EOF'
[Unit]
Description=MAMA AI Clinic - Web Application
After=llama-server.service
Requires=llama-server.service

[Service]
Type=simple
WorkingDirectory=/opt/pi-ai-clinic/app
ExecStart=/usr/bin/python3 -m gunicorn \
    --bind 0.0.0.0:80 \
    --workers 2 \
    --timeout 120 \
    "app:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable services
sudo chroot "${MOUNT_DIR}" systemctl enable llama-server.service
sudo chroot "${MOUNT_DIR}" systemctl enable pi-ai-clinic.service

# Copy networking config
sudo cp "${PROJECT_DIR}/networking/setup_hotspot.sh" "${MOUNT_DIR}/opt/pi-ai-clinic/"

# Unmount
echo "[6/6] Finalizing image..."
sudo umount "${MOUNT_DIR}/boot/firmware"
sudo umount "${MOUNT_DIR}"
sudo losetup -d "${LOOP_DEV}"

# Compress
echo "Compressing image..."
xz -T0 -k "${CUSTOM_IMG}"
mv "${CUSTOM_IMG}.xz" "${OUTPUT_DIR}/"

echo ""
echo "=== Build Complete ==="
echo "Image: ${OUTPUT_DIR}/${IMAGE_NAME}-${IMAGE_VERSION}.img.xz"
echo ""
echo "Flash with: xz -d ${OUTPUT_DIR}/${IMAGE_NAME}-${IMAGE_VERSION}.img.xz && sudo dd if=... of=/dev/sdX bs=4M status=progress"
echo "Or use: ./image/flash.sh ${OUTPUT_DIR}/${IMAGE_NAME}-${IMAGE_VERSION}.img.xz"
