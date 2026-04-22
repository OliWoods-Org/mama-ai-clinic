#!/usr/bin/env bash
# Configure Raspberry Pi as a WiFi Access Point with captive portal.
# Devices connect to "AI-Clinic" WiFi and are redirected to the web UI.

set -euo pipefail

SSID="${CLINIC_SSID:-AI-Clinic}"
INTERFACE="${WIFI_INTERFACE:-wlan0}"
IP_ADDR="192.168.4.1"
DHCP_RANGE_START="192.168.4.10"
DHCP_RANGE_END="192.168.4.100"

echo "=== MAMA AI Clinic -- WiFi Hotspot Setup ==="
echo "SSID: ${SSID}"
echo "Interface: ${INTERFACE}"
echo "IP: ${IP_ADDR}"
echo ""

# Install required packages
echo "[1/5] Installing hostapd and dnsmasq..."
sudo apt-get update -qq
sudo apt-get install -y -qq hostapd dnsmasq

# Stop services during configuration
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Configure static IP for wireless interface
echo "[2/5] Configuring static IP..."
sudo tee /etc/dhcpcd.conf.d/pi-ai-clinic.conf > /dev/null <<EOF
interface ${INTERFACE}
    static ip_address=${IP_ADDR}/24
    nohook wpa_supplicant
EOF

# Configure hostapd (WiFi AP)
echo "[3/5] Configuring hostapd..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
interface=${INTERFACE}
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
# Open network - no password required (captive portal UX)
auth_algs=1
wpa=0
# Country code - set to your deployment country
country_code=US
ieee80211n=1
ieee80211ac=0
EOF

sudo sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Configure dnsmasq (DHCP + DNS)
echo "[4/5] Configuring dnsmasq..."
sudo tee /etc/dnsmasq.d/pi-ai-clinic.conf > /dev/null <<EOF
interface=${INTERFACE}
dhcp-range=${DHCP_RANGE_START},${DHCP_RANGE_END},255.255.255.0,24h
# Redirect ALL DNS queries to the Pi (captive portal behavior)
address=/#/${IP_ADDR}
# Speed up DHCP
dhcp-authoritative
EOF

# Enable IP forwarding (not for internet - just for captive portal redirect)
echo "[5/5] Enabling services..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo ""
echo "=== Done. Reboot to activate. ==="
echo "After reboot, connect any device to '${SSID}' WiFi."
echo "All traffic will redirect to http://${IP_ADDR}"
