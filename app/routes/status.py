"""Status routes -- System health dashboard."""

import os
import platform
from flask import Blueprint, render_template, jsonify
from ..services import llm_client

bp = Blueprint("status", __name__, url_prefix="/status")


@bp.route("/")
def dashboard():
    return render_template("status.html")


@bp.route("/health", methods=["GET"])
def health():
    llm_ok = llm_client.health_check()

    # System metrics
    info = {
        "llm_server": "online" if llm_ok else "offline",
        "platform": platform.machine(),
        "python": platform.python_version(),
    }

    # CPU temperature (Raspberry Pi)
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_milli = int(f.read().strip())
            info["cpu_temp_c"] = round(temp_milli / 1000, 1)
    except (FileNotFoundError, ValueError):
        info["cpu_temp_c"] = None

    # Memory usage
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    meminfo[parts[0].rstrip(":")] = int(parts[1])
            total_mb = meminfo.get("MemTotal", 0) // 1024
            available_mb = meminfo.get("MemAvailable", 0) // 1024
            info["ram_total_mb"] = total_mb
            info["ram_available_mb"] = available_mb
            info["ram_used_pct"] = round((1 - available_mb / max(total_mb, 1)) * 100, 1)
    except (FileNotFoundError, ValueError):
        pass

    # Uptime
    try:
        with open("/proc/uptime") as f:
            uptime_secs = float(f.read().split()[0])
            hours = int(uptime_secs // 3600)
            mins = int((uptime_secs % 3600) // 60)
            info["uptime"] = f"{hours}h {mins}m"
    except (FileNotFoundError, ValueError):
        pass

    status_code = 200 if llm_ok else 503
    return jsonify(info), status_code
