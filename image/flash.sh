#!/usr/bin/env bash
# Flash a MAMA AI Clinic image to an SD card.
# Usage: ./flash.sh <image-file> [device]

set -euo pipefail

IMAGE="${1:-}"
DEVICE="${2:-}"

if [ -z "${IMAGE}" ]; then
    echo "Usage: ./flash.sh <image-file> [/dev/sdX]"
    echo ""
    echo "If device is not specified, will auto-detect removable media."
    exit 1
fi

if [ ! -f "${IMAGE}" ]; then
    echo "Error: Image file not found: ${IMAGE}"
    exit 1
fi

# Auto-detect SD card if device not specified
if [ -z "${DEVICE}" ]; then
    echo "Detecting removable media..."
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS
        DEVICE=$(diskutil list external | grep -m1 "/dev/disk" | awk '{print $1}')
    else
        # Linux
        DEVICE=$(lsblk -dpno NAME,RM | awk '$2==1 {print $1; exit}')
    fi

    if [ -z "${DEVICE}" ]; then
        echo "Error: No removable media detected. Insert SD card and try again."
        exit 1
    fi

    echo "Detected: ${DEVICE}"
    echo ""
fi

echo "=== MAMA AI Clinic -- SD Card Flasher ==="
echo "Image:  ${IMAGE}"
echo "Device: ${DEVICE}"
echo ""
echo "WARNING: This will ERASE ALL DATA on ${DEVICE}"
read -rp "Continue? [y/N] " confirm
if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Unmount any mounted partitions
echo "Unmounting..."
if [[ "$(uname)" == "Darwin" ]]; then
    diskutil unmountDisk "${DEVICE}" 2>/dev/null || true
    RAW_DEVICE="${DEVICE/disk/rdisk}"
else
    sudo umount "${DEVICE}"* 2>/dev/null || true
    RAW_DEVICE="${DEVICE}"
fi

# Decompress if needed
if [[ "${IMAGE}" == *.xz ]]; then
    echo "Decompressing..."
    xz -dk "${IMAGE}"
    IMAGE="${IMAGE%.xz}"
fi

# Flash
echo "Flashing (this takes 5-15 minutes)..."
if [[ "$(uname)" == "Darwin" ]]; then
    sudo dd if="${IMAGE}" of="${RAW_DEVICE}" bs=4m status=progress
    sudo sync
    diskutil eject "${DEVICE}"
else
    sudo dd if="${IMAGE}" of="${RAW_DEVICE}" bs=4M status=progress conv=fsync
    sudo sync
fi

echo ""
echo "=== Flash Complete ==="
echo "Remove the SD card, insert into Pi 5, and power on."
echo "Connect to WiFi network 'AI-Clinic' from any device."
