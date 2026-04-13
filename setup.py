import subprocess
import sys
import os
import json
from pathlib import Path

print("=" * 60)
print("  ALBEDO PRIME v2.0 — Installation")
print("  Master Ahmed's Private AI System")
print("=" * 60)

# ─── Step 1: Install Python dependencies ─────────────────────────────────────
print("\n[1/4] Installing Python dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
print("✅ Dependencies installed.")

# ─── Step 2: Install Playwright browsers ─────────────────────────────────────
print("\n[2/4] Installing Playwright browsers...")
subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
print("✅ Playwright browsers installed.")

# ─── Step 3: Configure API key ───────────────────────────────────────────────
print("\n[3/4] Configuring Gemini API key...")
CONFIG_DIR = Path(__file__).resolve().parent / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
API_FILE = CONFIG_DIR / "api_keys.json"

api_config = {
    "gemini_api_key": ""
}
API_FILE.write_text(json.dumps(api_config, indent=4), encoding="utf-8")
print(f"✅ API key saved to: {API_FILE}")

# ─── Step 4: Verify installation ─────────────────────────────────────────────
print("\n[4/4] Verifying installation...")
try:
    import pyaudio
    import google.genai
    import PIL
    import pyautogui
    import cv2
    import mss
    import psutil
    print("✅ All core modules verified.")
except ImportError as e:
    print(f"⚠️ Module missing: {e}")
    print("   Run: pip install <missing_module>")

# ─── Done ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ✅ ALBEDO PRIME v2.0 — Installation Complete!")
print("=" * 60)
print("\n  Launch: python main.py")
print("  Master Ahmed's AI is ready.")
print("=" * 60)
