# actions/pot_player.py — ALBEDO PotPlayer Controller
#
# Master Ahmed's preferred media player.
# Controls PotPlayer for music, videos, playlists, podcasts.
#
# Capabilities:
#   - Play music/video by file path or URL
#   - Search and play from local library
#   - Playlist management
#   - Playback control (play, pause, stop, next, prev, volume, seek)
#   - Open YouTube URLs directly in PotPlayer
#   - Control via keyboard shortcuts (PotPlayer hotkeys)

import os
import subprocess
import time
import pyautogui
from pathlib import Path

POTPLAYER_PATH = r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _is_potplayer_running() -> bool:
    """Check if PotPlayer is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq PotPlayerMini64.exe"],
            capture_output=True, text=True
        )
        return "PotPlayerMini64.exe" in result.stdout
    except Exception:
        return False


def _open_potplayer() -> bool:
    """Open PotPlayer if not running."""
    if _is_potplayer_running():
        return True
    try:
        if os.path.exists(POTPLAYER_PATH):
            subprocess.Popen([POTPLAYER_PATH])
            time.sleep(2)
            return True
        else:
            # Try via Windows search
            pyautogui.press("win")
            time.sleep(0.5)
            pyautogui.write("PotPlayer", interval=0.05)
            time.sleep(0.8)
            pyautogui.press("enter")
            time.sleep(2)
            return _is_potplayer_running()
    except Exception as e:
        print(f"[PotPlayer] ⚠️ Open failed: {e}")
        return False


def _focus_potplayer() -> bool:
    """Bring PotPlayer to foreground."""
    if not _is_potplayer_running():
        return _open_potplayer()
    try:
        pyautogui.hotkey("alt", "tab")
        time.sleep(0.3)
        return True
    except Exception:
        return False


def _send_hotkey(key: str) -> str:
    """Send a PotPlayer keyboard shortcut."""
    if not _focus_potplayer():
        return "PotPlayer is not running, sir."

    hotkey_map = {
        "play":        "space",
        "pause":       "space",
        "stop":        "stop",
        "next":        "right",
        "previous":    "left",
        "volume_up":   "up",
        "volume_down": "down",
        "mute":        "m",
        "fullscreen":  "enter",
        "screenshot":  "ctrl+e",
        "playlist":    "F5",
        "open_file":   "ctrl+f12",
        "seek_forward_5":  "shift+right",
        "seek_backward_5": "shift+left",
        "seek_forward_30": "ctrl+right",
        "seek_backward_30": "ctrl+left",
        "speed_up":    "shift+up",
        "speed_down":  "shift+down",
        "speed_reset": "shift+backspace",
        "repeat":      "l",
        "shuffle":     "ctrl+h",
        "subtitle":    "alt+h",
        "audio_track": "alt+l",
    }

    hotkey = hotkey_map.get(key.lower())
    if not hotkey:
        return f"Unknown PotPlayer command: {key}"

    try:
        if "+" in hotkey:
            keys = hotkey.split("+")
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(hotkey)
        time.sleep(0.2)
        return f"PotPlayer: {key} executed."
    except Exception as e:
        return f"PotPlayer hotkey failed: {e}"


def play_file(file_path: str) -> str:
    """Open a file in PotPlayer."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    try:
        subprocess.Popen([POTPLAYER_PATH, file_path])
        time.sleep(1)
        return f"Playing in PotPlayer: {Path(file_path).name}"
    except Exception as e:
        return f"PotPlayer open failed: {e}"


def play_url(url: str) -> str:
    """Open a URL (YouTube, stream, etc.) in PotPlayer."""
    try:
        subprocess.Popen([POTPLAYER_PATH, url])
        time.sleep(2)
        return f"Playing URL in PotPlayer: {url[:80]}"
    except Exception as e:
        return f"PotPlayer URL open failed: {e}"


def play_music(query: str, search_paths: list = None) -> str:
    """
    Search for music in common locations and play.
    query: song name, artist, or genre
    """
    if search_paths is None:
        search_paths = [
            Path.home() / "Music",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path("F:\\AHMED\\best"),  # Master Ahmed's music folder
        ]

    query_lower = query.lower()
    found_files = []

    for folder in search_paths:
        if not folder.exists():
            continue
        try:
            for f in folder.rglob("*"):
                if f.is_file() and f.suffix.lower() in (".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg", ".wma", ".mp4", ".mkv", ".avi"):
                    if any(word in f.name.lower() for word in query_lower.split()):
                        found_files.append(str(f))
                        if len(found_files) >= 10:
                            break
        except Exception:
            continue
        if found_files:
            break

    if found_files:
        # Play the first match
        result = play_file(found_files[0])
        if len(found_files) > 1:
            result += f" ({len(found_files)} matches found, playing first)"
        return result

    return f"No music found matching '{query}' in your library, sir. Try a URL or file path."


def get_playlist() -> str:
    """Get current playlist info (opens playlist window)."""
    if not _focus_potplayer():
        return "PotPlayer is not running, sir."

    try:
        pyautogui.press("F5")  # Open playlist
        time.sleep(0.5)
        return "Playlist opened in PotPlayer. You can see the current queue, sir."
    except Exception as e:
        return f"Could not open playlist: {e}"


def pot_player(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    PotPlayer Controller — Master Ahmed's preferred media player.

    parameters:
        action  : play_file | play_url | play_music | play | pause | stop |
                  next | previous | volume_up | volume_down | mute |
                  fullscreen | screenshot | playlist | seek_forward | seek_backward |
                  speed_up | speed_down | repeat | shuffle | open
        file    : File path for play_file
        url     : URL for play_url (YouTube, stream, etc.)
        query   : Search query for play_music (song name, artist)
        key     : Custom hotkey name
    """
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if player:
        player.write_log(f"[PotPlayer] {action}")

    print(f"[PotPlayer] ▶️ Action: {action}  Params: {params}")

    try:
        if action == "open" or action == "launch":
            if _open_potplayer():
                return "PotPlayer opened, sir."
            return "Could not open PotPlayer, sir."

        elif action == "play_file":
            file_path = params.get("file", "")
            if not file_path:
                return "Please provide a file path, sir."
            return play_file(file_path)

        elif action == "play_url":
            url = params.get("url", "")
            if not url:
                return "Please provide a URL, sir."
            return play_url(url)

        elif action == "play_music":
            query = params.get("query", "")
            if not query:
                return "Please provide a song name or artist, sir."
            return play_music(query)

        elif action in ("play", "pause", "stop", "next", "previous",
                        "volume_up", "volume_down", "mute", "fullscreen",
                        "screenshot", "playlist", "repeat", "shuffle"):
            return _send_hotkey(action)

        elif action == "seek_forward":
            return _send_hotkey("seek_forward_5")

        elif action == "seek_backward":
            return _send_hotkey("seek_backward_5")

        elif action == "speed_up":
            return _send_hotkey("speed_up")

        elif action == "speed_down":
            return _send_hotkey("speed_down")

        else:
            # Try as hotkey
            return _send_hotkey(action)

    except Exception as e:
        return f"PotPlayer error: {e}"
