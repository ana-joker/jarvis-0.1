# actions/system_monitor.py — ALBEDO System Monitor
#
# Real-time system monitoring: CPU, GPU, RAM, disk, network, temps.
# Uses psutil, wmic, and nvidia-smi for comprehensive monitoring.

import subprocess
import time
from pathlib import Path

try:
    import psutil
    _PSUTIL_OK = True
except ImportError:
    _PSUTIL_OK = False


def _get_cpu_info() -> dict:
    """Get CPU usage and info."""
    if not _PSUTIL_OK:
        return {"error": "psutil not installed"}

    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "freq_current": f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "N/A",
    }


def _get_ram_info() -> dict:
    """Get RAM usage."""
    if not _PSUTIL_OK:
        return {"error": "psutil not installed"}

    mem = psutil.virtual_memory()
    return {
        "total_gb": f"{mem.total / (1024**3):.1f} GB",
        "used_gb": f"{mem.used / (1024**3):.1f} GB",
        "available_gb": f"{mem.available / (1024**3):.1f} GB",
        "usage_percent": mem.percent,
    }


def _get_disk_info() -> dict:
    """Get disk usage for all drives."""
    if not _PSUTIL_OK:
        return {"error": "psutil not installed"}

    disks = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.device] = {
                "total_gb": f"{usage.total / (1024**3):.1f} GB",
                "used_gb": f"{usage.used / (1024**3):.1f} GB",
                "free_gb": f"{usage.free / (1024**3):.1f} GB",
                "usage_percent": usage.percent,
            }
        except PermissionError:
            pass
    return disks


def _get_gpu_info() -> dict:
    """Get GPU info via nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            gpus = []
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 6:
                    gpus.append({
                        "name": parts[0],
                        "memory_total_mb": parts[1],
                        "memory_used_mb": parts[2],
                        "memory_free_mb": parts[3],
                        "utilization_percent": parts[4],
                        "temperature_c": parts[5],
                    })
            return {"gpus": gpus}
    except Exception:
        pass
    return {"gpus": []}


def _get_network_info() -> dict:
    """Get network I/O stats."""
    if not _PSUTIL_OK:
        return {"error": "psutil not installed"}

    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": f"{net.bytes_sent / (1024**2):.1f} MB",
        "bytes_recv_mb": f"{net.bytes_recv / (1024**2):.1f} MB",
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


def _get_top_processes(count: int = 10) -> list:
    """Get top processes by CPU usage."""
    if not _PSUTIL_OK:
        return []

    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"] or 0,
                "memory_percent": info["memory_percent"] or 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return procs[:count]


def _get_battery_info() -> dict:
    """Get battery info (laptops only)."""
    if not _PSUTIL_OK:
        return {"error": "psutil not installed"}

    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "secsleft": f"{battery.secsleft // 60} minutes" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited",
                "power_plugged": battery.power_plugged,
            }
    except Exception:
        pass
    return {"status": "No battery or desktop PC"}


def system_monitor(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    System Monitor — Real-time PC health check.

    parameters:
        action : full | cpu | ram | disk | gpu | network | processes | battery | temps
        count  : Number of top processes (default: 10)
    """
    params = parameters or {}
    action = params.get("action", "full").lower().strip()

    if player:
        player.write_log(f"[SysMonitor] {action}")

    print(f"[SysMonitor] ▶️ Action: {action}")

    try:
        if action == "full" or action == "status":
            cpu = _get_cpu_info()
            ram = _get_ram_info()
            gpu = _get_gpu_info()
            battery = _get_battery_info()

            lines = [
                f"CPU: {cpu.get('usage_percent', 'N/A')}% | {cpu.get('cores_physical', '?')} cores @ {cpu.get('freq_current', '?')}",
                f"RAM: {ram.get('used_gb', '?')} / {ram.get('total_gb', '?')} ({ram.get('usage_percent', '?')}%)",
            ]

            gpus = gpu.get("gpus", [])
            for i, g in enumerate(gpus):
                lines.append(f"GPU{i}: {g['name']} | {g['utilization_percent']}% | {g['temperature_c']}°C | {g['memory_used_mb']}/{g['memory_total_mb']} MB")

            if battery.get("percent"):
                lines.append(f"Battery: {battery['percent']}% | {'Charging' if battery['power_plugged'] else 'Discharging'}")

            return "\n".join(lines)

        elif action == "cpu":
            cpu = _get_cpu_info()
            return f"CPU: {cpu['usage_percent']}% usage | {cpu['cores_physical']} cores @ {cpu['freq_current']}"

        elif action == "ram":
            ram = _get_ram_info()
            return f"RAM: {ram['used_gb']} / {ram['total_gb']} ({ram['usage_percent']}% used)"

        elif action == "disk":
            disks = _get_disk_info()
            lines = []
            for drive, info in disks.items():
                lines.append(f"{drive}: {info['used_gb']} / {info['total_gb']} ({info['usage_percent']}%)")
            return "\n".join(lines) if lines else "No disk info available."

        elif action == "gpu":
            gpu = _get_gpu_info()
            gpus = gpu.get("gpus", [])
            if not gpus:
                return "No NVIDIA GPU detected, sir."
            lines = []
            for i, g in enumerate(gpus):
                lines.append(f"GPU{i}: {g['name']}")
                lines.append(f"  Usage: {g['utilization_percent']}% | Temp: {g['temperature_c']}°C")
                lines.append(f"  Memory: {g['memory_used_mb']} / {g['memory_total_mb']} MB")
            return "\n".join(lines)

        elif action == "network":
            net = _get_network_info()
            return f"Network: ↑ {net['bytes_sent_mb']} sent | ↓ {net['bytes_recv_mb']} received"

        elif action == "processes" or action == "top":
            count = int(params.get("count", 10))
            procs = _get_top_processes(count)
            lines = [f"Top {count} processes by CPU:"]
            for p in procs:
                lines.append(f"  {p['name']:20s} | CPU: {p['cpu_percent']:5.1f}% | RAM: {p['memory_percent']:4.1f}%")
            return "\n".join(lines)

        elif action == "battery":
            battery = _get_battery_info()
            if battery.get("percent"):
                return f"Battery: {battery['percent']}% | {'Charging' if battery['power_plugged'] else 'Discharging'} | {battery['secsleft']} remaining"
            return "No battery detected (desktop PC), sir."

        elif action == "temps":
            gpu = _get_gpu_info()
            gpus = gpu.get("gpus", [])
            if gpus:
                lines = ["Temperatures:"]
                for i, g in enumerate(gpus):
                    lines.append(f"  GPU{i}: {g['temperature_c']}°C")
                return "\n".join(lines)
            return "Temperature monitoring requires NVIDIA GPU, sir."

        else:
            return f"Unknown monitor action: '{action}', sir."

    except Exception as e:
        return f"System monitor error: {e}, sir."
