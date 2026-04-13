# jarvis_skill.py — Qwen Code CLI's interface to JARVIS Voice Assistant
#
# This is the file Qwen imports to use JARVIS as a skill.
# Place: C:\Users\Ahmed El3nany\.qwen\skills\jarvis-voice\jarvis_skill.py
#
# Usage in Qwen:
#   from .qwen.skills.jarvis-voice.jarvis_skill import JarvisSkill
#   
#   jarvis = JarvisSkill()
#   jarvis.open_app("Chrome")
#   jarvis.search("Python tutorials")
#   jarvis.analyze_screen("What's on my screen?")
#
# Master Ahmed's JARVIS-QWEN Unified System v1.0

import sys
import json
from pathlib import Path

# ─── Path Setup ───────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).resolve().parent
BRIDGE_DIR = SKILL_DIR / "bridge"
MEMORY_DIR = SKILL_DIR / "memory"

# Ensure dirs exist
BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Add skill dir to path for imports
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))


class JarvisSkill:
    """
    Qwen's primary interface to JARVIS Voice Assistant.
    
    This class provides:
    1. Direct action execution (sync)
    2. Async task submission (for voice/screen)
    3. Memory synchronization
    4. Qwen delegation (JARVIS → Qwen)
    
    All 16 JARVIS capabilities available as methods.
    """

    def __init__(self):
        self._executor = None
        self._load_executor()

    def _load_executor(self):
        """Lazy-load the executor."""
        try:
            from executor import get_executor
            self._executor = get_executor()
            print("[JarvisSkill] ✅ JARVIS executor loaded")
        except Exception as e:
            print(f"[JarvisSkill] ⚠️ Executor not available: {e}")
            self._executor = None

    def _ensure_executor(self):
        if self._executor is None:
            self._load_executor()
        if self._executor is None:
            raise RuntimeError("JARVIS executor not available. Check installation.")
        return self._executor

    # ─── Voice & Vision ─────────────────────────────────────────────────

    def speak(self, text: str) -> str:
        """JARVIS speaks the given text aloud."""
        return self._ensure_executor().submit_speak_task(text)

    def analyze_screen(self, question: str) -> str:
        """Capture screen and Gemini analyzes it."""
        return self._ensure_executor().analyze_screen(question)

    def analyze_camera(self, question: str) -> str:
        """Capture camera and Gemini analyzes it."""
        return self._ensure_executor().analyze_camera(question)

    # ─── Applications ───────────────────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        """Open any Windows application."""
        return self._ensure_executor().open_app(app_name)

    # ─── Web & Search ───────────────────────────────────────────────────

    def search_web(self, query: str) -> str:
        """Search the web using Gemini Google Search."""
        return self._ensure_executor().search_web(query)

    def get_weather(self, city: str) -> str:
        """Get weather report for a city."""
        return self._ensure_executor().get_weather(city)

    def find_flights(self, origin: str, destination: str, date: str,
                     return_date: str = None, cabin: str = "economy") -> str:
        """Search Google Flights."""
        params = {"origin": origin, "destination": destination, "date": date, "cabin": cabin}
        if return_date:
            params["return_date"] = return_date
        return self._ensure_executor().find_flights(**params)

    # ─── Messaging ──────────────────────────────────────────────────────

    def send_message(self, receiver: str, message: str, platform: str = "WhatsApp") -> str:
        """Send message via WhatsApp/Telegram/Instagram."""
        return self._ensure_executor().send_message(receiver, message, platform)

    # ─── Reminders ──────────────────────────────────────────────────────

    def set_reminder(self, date: str, time: str, message: str) -> str:
        """Schedule a Windows reminder."""
        return self._ensure_executor().set_reminder(date, time, message)

    # ─── Browser ────────────────────────────────────────────────────────

    def browser_go_to(self, url: str) -> str:
        """Navigate to a URL."""
        return self._ensure_executor().control_browser("go_to", url=url)

    def browser_search(self, query: str) -> str:
        """Search the web in browser."""
        return self._ensure_executor().control_browser("search", query=query)

    def browser_click(self, text: str = None, selector: str = None) -> str:
        """Click an element by text or CSS selector."""
        params = {}
        if text: params["text"] = text
        if selector: params["selector"] = selector
        return self._ensure_executor().control_browser("click", **params)

    def browser_type(self, text: str, selector: str = None) -> str:
        """Type text into an element."""
        params = {"text": text}
        if selector: params["selector"] = selector
        return self._ensure_executor().control_browser("type", **params)

    def browser_scroll(self, direction: str = "down") -> str:
        """Scroll the page."""
        return self._ensure_executor().control_browser("scroll", direction=direction)

    def browser_get_text(self) -> str:
        """Get all text from the current page."""
        return self._ensure_executor().control_browser("get_text")

    def browser_close(self) -> str:
        """Close the browser."""
        return self._ensure_executor().control_browser("close")

    # ─── File Management ────────────────────────────────────────────────

    def list_files(self, path: str = "desktop") -> str:
        """List files in a directory."""
        return self._ensure_executor().manage_files("list", path=path)

    def create_file(self, path: str, name: str, content: str = "") -> str:
        """Create a new file."""
        return self._ensure_executor().manage_files("create_file", path=path, name=name, content=content)

    def read_file(self, path: str, name: str) -> str:
        """Read file contents."""
        return self._ensure_executor().manage_files("read", path=path, name=name)

    def write_file(self, path: str, name: str, content: str) -> str:
        """Write content to a file."""
        return self._ensure_executor().manage_files("write", path=path, name=name, content=content)

    def delete_file(self, path: str, name: str) -> str:
        """Delete a file (moves to recycle bin)."""
        return self._ensure_executor().manage_files("delete", path=path, name=name)

    def find_files(self, name: str = "", extension: str = "", path: str = "home") -> str:
        """Search for files by name or extension."""
        return self._ensure_executor().manage_files("find", name=name, extension=extension, path=path)

    def organize_desktop(self) -> str:
        """Organize desktop files into folders by type."""
        return self._ensure_executor().manage_files("organize_desktop")

    def disk_usage(self, path: str = "home") -> str:
        """Get disk usage information."""
        return self._ensure_executor().manage_files("disk_usage", path=path)

    # ─── Command Line ───────────────────────────────────────────────────

    def run_command(self, task: str) -> str:
        """Execute a CMD command (natural language description)."""
        return self._ensure_executor().run_command(task)

    # ─── Computer Control ───────────────────────────────────────────────

    def volume_up(self) -> str:
        return self._ensure_executor().control_settings("volume_up")

    def volume_down(self) -> str:
        return self._ensure_executor().control_settings("volume_down")

    def mute(self) -> str:
        return self._ensure_executor().control_settings("mute")

    def set_volume(self, value: int) -> str:
        return self._ensure_executor().control_settings("volume_set", value=value)

    def close_app(self) -> str:
        return self._ensure_executor().control_settings("close_app")

    def full_screen(self) -> str:
        return self._ensure_executor().control_settings("full_screen")

    def minimize_window(self) -> str:
        return self._ensure_executor().control_settings("minimize")

    def maximize_window(self) -> str:
        return self._ensure_executor().control_settings("maximize")

    def take_screenshot(self) -> str:
        return self._ensure_executor().control_settings("screenshot")

    def lock_screen(self) -> str:
        return self._ensure_executor().control_settings("lock_screen")

    def refresh_page(self) -> str:
        return self._ensure_executor().control_settings("refresh_page")

    def close_tab(self) -> str:
        return self._ensure_executor().control_settings("close_tab")

    def new_tab(self) -> str:
        return self._ensure_executor().control_settings("new_tab")

    def scroll_down(self) -> str:
        return self._ensure_executor().control_settings("scroll_down")

    def scroll_up(self) -> str:
        return self._ensure_executor().control_settings("scroll_up")

    def type_text(self, text: str) -> str:
        return self._ensure_executor().control_settings("type_text", value=text)

    # ─── Desktop Management ─────────────────────────────────────────────

    def set_wallpaper(self, path: str) -> str:
        return self._ensure_executor().manage_desktop("wallpaper", path=path)

    def set_wallpaper_url(self, url: str) -> str:
        return self._ensure_executor().manage_desktop("wallpaper_url", url=url)

    def organize_desktop(self) -> str:
        return self._ensure_executor().manage_desktop("organize")

    def clean_desktop(self) -> str:
        return self._ensure_executor().manage_desktop("clean")

    def list_desktop(self) -> str:
        return self._ensure_executor().manage_desktop("list")

    def desktop_stats(self) -> str:
        return self._ensure_executor().manage_desktop("stats")

    # ─── Code & Development ─────────────────────────────────────────────

    def write_code(self, description: str, language: str = "python") -> str:
        """Generate code and save to file."""
        return self._ensure_executor().write_code(description, language)

    def build_project(self, description: str, language: str = "python") -> str:
        """Build a multi-file project with auto-fix."""
        return self._ensure_executor().build_project(description, language)

    # ─── YouTube ────────────────────────────────────────────────────────

    def youtube_play(self, query: str) -> str:
        """Search and play a YouTube video."""
        return self._ensure_executor().api.execute("youtube", {
            "action": "play", "query": query
        })

    def youtube_summarize(self, url: str = None) -> str:
        """Summarize a YouTube video via transcript."""
        params = {"action": "summarize"}
        if url:
            params["url"] = url
        return self._ensure_executor().api.execute("youtube", params)

    def youtube_trending(self, region: str = "US") -> str:
        """Get trending YouTube videos."""
        return self._ensure_executor().api.execute("youtube", {
            "action": "trending", "region": region
        })

    # ─── Async Task System ──────────────────────────────────────────────

    def submit_task(self, goal: str, priority: str = "normal") -> str:
        """Submit an async task for JARVIS to execute."""
        from qwen_bridge import submit_task, TaskPriority
        p_map = {"low": TaskPriority.LOW, "normal": TaskPriority.NORMAL, "high": TaskPriority.HIGH}
        return submit_task(goal, p_map.get(priority, TaskPriority.NORMAL))

    def wait_for_task(self, task_id: str, timeout: int = 120) -> dict:
        """Wait for a submitted task to complete."""
        return self._ensure_executor().wait_for_result(task_id, timeout)

    # ─── Memory ─────────────────────────────────────────────────────────

    def sync_memory(self) -> dict:
        """Sync JARVIS memory with Qwen's Akashic memory."""
        from qwen_bridge import sync_memory_to_qwen, sync_memory_from_qwen
        sync_memory_to_qwen()
        sync_memory_from_qwen()
        return self._ensure_executor().get_unified_memory()

    def get_memory(self) -> dict:
        """Get unified memory (JARVIS + Qwen)."""
        from qwen_bridge import get_unified_memory
        return get_unified_memory()

    # ─── Utility ────────────────────────────────────────────────────────

    def list_actions(self) -> list:
        """List all available JARVIS actions."""
        return self._ensure_executor().list_actions()

    def status(self) -> dict:
        """Get JARVIS skill status."""
        return {
            "executor_loaded": self._executor is not None,
            "actions_available": len(self.list_actions()) if self._executor else 0,
            "skill_dir": str(SKILL_DIR),
        }


# ─── Module-level singleton ──────────────────────────────────────────────────

_jarvis = None

def get_jarvis() -> JarvisSkill:
    """Get or create the JARVIS skill singleton."""
    global _jarvis
    if _jarvis is None:
        _jarvis = JarvisSkill()
    return _jarvis


# Convenience: `from jarvis_skill import jarvis`
jarvis = None  # Lazy-loaded on first access

def __getattr__(name):
    global jarvis
    if name == "jarvis":
        if jarvis is None:
            jarvis = get_jarvis()
        return jarvis
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


if __name__ == "__main__":
    print("=" * 60)
    print("  JARVIS Skill — Qwen Integration Test")
    print("=" * 60)

    js = JarvisSkill()
    print(f"\n✅ Status: {js.status()}")
    print(f"\n✅ Actions: {js.list_actions()}")
    print("\n✅ JARVIS Skill ready for Qwen Code CLI!")
