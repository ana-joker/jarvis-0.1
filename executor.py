# executor.py — JARVIS Voice Skill Executor for Qwen Code CLI
#
# This is how Qwen calls JARVIS capabilities directly.
# Qwen imports this module and uses the JarvisSkillAPI to:
#   - Open apps, control browser, manage files
#   - Run commands, analyze screen, send messages
#   - Build projects, find flights, control PC settings
#
# Master Ahmed's JARVIS-QWEN Unified System v1.0

import sys
from pathlib import Path

# Add skill directory to path
SKILL_DIR = Path(__file__).resolve().parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from qwen_bridge import (
    JarvisSkillAPI,
    submit_task,
    get_task_result,
    submit_to_qwen,
    get_qwen_result,
    sync_memory_to_qwen,
    sync_memory_from_qwen,
    get_unified_memory,
    TaskPriority,
    log,
)


class JarvisVoiceExecutor:
    """
    Qwen's interface to JARVIS voice assistant capabilities.
    
    Usage:
        executor = JarvisVoiceExecutor()
        
        # Direct action execution
        result = executor.open_app("Chrome")
        result = executor.search_web("Python tutorials")
        result = executor.get_weather("Istanbul")
        result = executor.analyze_screen("What code is on screen?")
        
        # Async task submission (for voice/screen actions)
        task_id = executor.submit_voice_task("Open Spotify and play lofi")
        result = executor.wait_for_result(task_id)
        
        # Delegate to Qwen (JARVIS → Qwen)
        task_id = executor.delegate_to_qwen("Research AI trends and save to file")
    """

    def __init__(self):
        self.api = JarvisSkillAPI()
        log("[Executor] JARVIS Voice Executor initialized")

    # ─── Direct Actions (Synchronous) ─────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        """Open any Windows application."""
        return self.api.open_app(app_name)

    def search_web(self, query: str) -> str:
        """Search the web using Gemini Google Search."""
        return self.api.search_web(query)

    def get_weather(self, city: str) -> str:
        """Get weather report for a city."""
        return self.api.get_weather(city)

    def send_message(self, receiver: str, message: str, platform: str = "WhatsApp") -> str:
        """Send message via WhatsApp/Telegram/Instagram."""
        return self.api.send_message(receiver, message, platform)

    def set_reminder(self, date: str, time: str, message: str) -> str:
        """Schedule a Windows reminder."""
        return self.api.set_reminder(date, time, message)

    def control_browser(self, action: str, **kwargs) -> str:
        """
        Control web browser.
        Actions: go_to, search, click, type, scroll, get_text, press, close
        """
        return self.api.control_browser(action, **kwargs)

    def manage_files(self, action: str, **kwargs) -> str:
        """
        File/folder management.
        Actions: list, create_file, create_folder, delete, move, copy,
                 rename, read, write, find, largest, disk_usage, organize_desktop
        """
        return self.api.manage_files(action, **kwargs)

    def run_command(self, task: str) -> str:
        """Execute a CMD/terminal command (natural language)."""
        return self.api.run_command(task)

    def control_computer(self, action: str, **kwargs) -> str:
        """
        Direct computer control.
        Actions: type, click, hotkey, scroll, screenshot, move, copy, paste, etc.
        """
        return self.api.control_computer(action, **kwargs)

    def control_settings(self, action: str, **kwargs) -> str:
        """
        Computer settings & UI controls.
        Actions: volume_up, volume_down, mute, brightness, close_app,
                 full_screen, minimize, maximize, screenshot, lock, restart, shutdown, etc.
        """
        return self.api.control_settings(action, **kwargs)

    def manage_desktop(self, action: str, **kwargs) -> str:
        """
        Desktop management.
        Actions: wallpaper, wallpaper_url, organize, clean, list, stats, task
        """
        return self.api.manage_desktop(action, **kwargs)

    def write_code(self, description: str, language: str = "python") -> str:
        """Generate and save code via Gemini."""
        return self.api.write_code(description, language)

    def build_project(self, description: str, language: str = "python") -> str:
        """Build a multi-file project (dev_agent)."""
        return self.api.build_project(description, language)

    def find_flights(self, origin: str, destination: str, date: str, **kwargs) -> str:
        """Search Google Flights."""
        return self.api.find_flights(origin, destination, date, **kwargs)

    def analyze_screen(self, question: str) -> str:
        """Capture screen and ask Gemini to analyze it."""
        return self.api.analyze_screen(question)

    def analyze_camera(self, question: str) -> str:
        """Capture camera and ask Gemini to analyze it."""
        return self.api.analyze_camera(question)

    def list_actions(self) -> list:
        """List all available JARVIS actions."""
        return self.api.list_actions()

    # ─── Async Task Submission (for voice/screen actions) ─────────────────

    def submit_voice_task(self, goal: str, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit a task for JARVIS to execute (async)."""
        return submit_task(goal, priority, action="execute")

    def submit_speak_task(self, text: str) -> str:
        """JARVIS speaks the given text."""
        return submit_task(text, TaskPriority.HIGH, action="speak")

    def submit_vision_task(self, question: str) -> str:
        """JARVIS captures screen and analyzes."""
        return submit_task(question, TaskPriority.NORMAL, action="vision")

    def wait_for_result(self, task_id: str, timeout: int = 120) -> dict:
        """Wait for a submitted task to complete."""
        return get_task_result(task_id, timeout)

    # ─── Qwen Delegation (JARVIS → Qwen) ──────────────────────────────────

    def delegate_to_qwen(self, goal: str, priority: str = "normal") -> str:
        """Delegate a complex task to Qwen for execution."""
        return submit_to_qwen(goal, priority)

    def get_qwen_result(self, task_id: str, timeout: int = 300) -> dict:
        """Wait for Qwen to complete a delegated task."""
        return get_qwen_result(task_id, timeout)

    # ─── Memory ───────────────────────────────────────────────────────────

    def sync_memory_to_qwen(self) -> dict:
        """Sync JARVIS memory to Qwen."""
        return sync_memory_to_qwen()

    def sync_memory_from_qwen(self) -> dict:
        """Sync Qwen memory to JARVIS."""
        return sync_memory_from_qwen()

    def get_unified_memory(self) -> dict:
        """Get merged memory from both systems."""
        return get_unified_memory()


# ─── Module-level convenience functions ──────────────────────────────────────

_executor = None

def get_executor() -> JarvisVoiceExecutor:
    """Singleton accessor."""
    global _executor
    if _executor is None:
        _executor = JarvisVoiceExecutor()
    return _executor


# Direct function shortcuts
def jarvis_open_app(app_name: str) -> str:
    return get_executor().open_app(app_name)

def jarvis_search(query: str) -> str:
    return get_executor().search_web(query)

def jarvis_weather(city: str) -> str:
    return get_executor().get_weather(city)

def jarvis_send_message(receiver: str, message: str, platform: str = "WhatsApp") -> str:
    return get_executor().send_message(receiver, message, platform)

def jarvis_reminder(date: str, time: str, message: str) -> str:
    return get_executor().set_reminder(date, time, message)

def jarvis_browser(action: str, **kwargs) -> str:
    return get_executor().control_browser(action, **kwargs)

def jarvis_files(action: str, **kwargs) -> str:
    return get_executor().manage_files(action, **kwargs)

def jarvis_cmd(task: str) -> str:
    return get_executor().run_command(task)

def jarvis_computer(action: str, **kwargs) -> str:
    return get_executor().control_computer(action, **kwargs)

def jarvis_settings(action: str, **kwargs) -> str:
    return get_executor().control_settings(action, **kwargs)

def jarvis_desktop(action: str, **kwargs) -> str:
    return get_executor().manage_desktop(action, **kwargs)

def jarvis_code(description: str, language: str = "python") -> str:
    return get_executor().write_code(description, language)

def jarvis_build(description: str, language: str = "python") -> str:
    return get_executor().build_project(description, language)

def jarvis_flights(origin: str, destination: str, date: str, **kwargs) -> str:
    return get_executor().find_flights(origin, destination, date, **kwargs)

def jarvis_screen(question: str) -> str:
    return get_executor().analyze_screen(question)

def jarvis_camera(question: str) -> str:
    return get_executor().analyze_camera(question)


if __name__ == "__main__":
    print("=" * 60)
    print("  JARVIS Voice Skill — Executor Test")
    print("=" * 60)

    executor = get_executor()
    actions = executor.list_actions()
    print(f"\n✅ {len(actions)} actions available:")
    for a in actions:
        print(f"  • {a}")

    print("\n✅ Executor ready for Qwen integration!")
