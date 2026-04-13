# qwen_bridge.py — Qwen Code CLI ↔ Mark-XXX (JARVIS) Bidirectional Bridge
#
# This is the CENTRAL integration layer. It allows:
#   1. Qwen → JARVIS: Qwen sends voice/screen/browser commands to JARVIS
#   2. JARVIS → Qwen: JARVIS delegates complex tasks to Qwen's agent_task
#   3. Shared Memory: Both agents read/write to unified memory
#
# Architecture:
#   - File-based task queue (JSON) for reliability
#   - Named pipe for real-time communication (optional, faster)
#   - Shared memory bridge (Akashic DB + long_term.json)
#
# Master Ahmed's JARVIS-QWEN Unified System v1.0

import json
import os
import sys
import time
import threading
import uuid
from pathlib import Path
from datetime import datetime
from typing import Callable, Any, Optional
from enum import Enum

# ─── Path Setup ───────────────────────────────────────────────────────────────

def get_base_dir() -> Path:
    """Returns the jarvis-voice skill directory."""
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()
BRIDGE_DIR = BASE_DIR / "bridge"
TASK_QUEUE = BRIDGE_DIR / "task_queue.json"
RESULT_QUEUE = BRIDGE_DIR / "result_queue.json"
STATUS_FILE = BRIDGE_DIR / "status.json"
SHARED_MEMORY = BRIDGE_DIR / "shared_memory.json"
LOG_FILE = BRIDGE_DIR / "bridge.log"

# Qwen paths
QWEN_BASE = Path.home() / ".qwen"
QWEN_MEMORY = QWEN_BASE / "memory" / "akashic"
QWEN_MARK_XXX_MEMORY = BASE_DIR / "memory" / "long_term.json"

# Ensure directories
BRIDGE_DIR.mkdir(parents=True, exist_ok=True)


# ─── Logging ──────────────────────────────────────────────────────────────────

def log(message: str):
    """Append to bridge log file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ─── Task Queue (Qwen → JARVIS) ──────────────────────────────────────────────

class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def submit_task(
    goal: str,
    priority: TaskPriority = TaskPriority.NORMAL,
    action: str = "execute",
    params: dict = None,
) -> str:
    """
    Qwen submits a task for JARVIS to execute via voice/actions.
    
    Actions:
    - "execute" : Run a JARVIS action (open_app, browser_control, etc.)
    - "speak"   : JARVIS speaks the given text
    - "vision"  : JARVIS captures screen/camera and analyzes
    - "voice_session" : Start full voice session (blocks)
    """
    task_id = str(uuid.uuid4())[:8]
    task = {
        "task_id": task_id,
        "goal": goal,
        "action": action,
        "params": params or {},
        "priority": priority.value,
        "status": TaskStatus.PENDING.value,
        "submitted_by": "qwen",
        "submitted_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    # Append to queue file
    tasks = _load_json(TASK_QUEUE, [])
    tasks.append(task)
    _save_json(TASK_QUEUE, tasks)

    log(f"[Qwen→JARVIS] Task submitted: [{task_id}] {goal[:80]}")
    return task_id


def get_task_result(task_id: str, timeout: int = 120) -> Optional[dict]:
    """Qwen waits for JARVIS to complete a task."""
    start = time.time()
    while time.time() - start < timeout:
        results = _load_json(RESULT_QUEUE, [])
        for r in results:
            if r.get("task_id") == task_id:
                log(f"[JARVIS→Qwen] Result received: [{task_id}]")
                return r
        time.sleep(0.5)

    log(f"[JARVIS→Qwen] Timeout waiting for: [{task_id}]")
    return None


# ─── Task Queue (JARVIS → Qwen) ──────────────────────────────────────────────

def submit_to_qwen(
    goal: str,
    priority: str = "normal",
    context: dict = None,
) -> str:
    """
    JARVIS delegates a complex task to Qwen.
    Called from main.py's agent_task handler.
    """
    task_id = str(uuid.uuid4())[:8]
    task = {
        "task_id": task_id,
        "goal": goal,
        "priority": priority,
        "context": context or {},
        "status": TaskStatus.PENDING.value,
        "submitted_by": "jarvis",
        "submitted_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    qwen_queue = QWEN_BASE / "jarvis_tasks.json"
    tasks = _load_json(qwen_queue, [])
    tasks.append(task)
    _save_json(qwen_queue, tasks)

    log(f"[JARVIS→Qwen] Task delegated: [{task_id}] {goal[:80]}")
    return task_id


def get_qwen_result(task_id: str, timeout: int = 300) -> Optional[dict]:
    """JARVIS waits for Qwen to complete a delegated task."""
    start = time.time()
    while time.time() - start < timeout:
        qwen_results = QWEN_BASE / "jarvis_results.json"
        results = _load_json(qwen_results, [])
        for r in results:
            if r.get("task_id") == task_id:
                log(f"[Qwen→JARVIS] Result received: [{task_id}]")
                return r
        time.sleep(1.0)

    log(f"[Qwen→JARVIS] Timeout waiting for: [{task_id}]")
    return None


# ─── Shared Memory Bridge ────────────────────────────────────────────────────

def sync_memory_to_qwen():
    """Copy Mark-XXX's long_term.json → Qwen's shared memory."""
    try:
        if QWEN_MARK_XXX_MEMORY.exists():
            mark_data = json.loads(
                QWEN_MARK_XXX_MEMORY.read_text(encoding="utf-8")
            )
            shared = _load_json(SHARED_MEMORY, {})
            shared["jarvis_memory"] = mark_data
            shared["last_sync"] = datetime.now().isoformat()
            _save_json(SHARED_MEMORY, shared)
            log("[Memory] JARVIS → Qwen sync complete")
            return mark_data
    except Exception as e:
        log(f"[Memory] Sync failed: {e}")
    return {}


def sync_memory_from_qwen():
    """Copy Qwen's Akashic memory → Mark-XXX's long_term.json."""
    try:
        shared = _load_json(SHARED_MEMORY, {})
        qwen_data = shared.get("qwen_memory", {})
        if qwen_data:
            # Merge into Mark-XXX memory
            mark_data = _load_json(QWEN_MARK_XXX_MEMORY, {
                "identity": {}, "preferences": {},
                "relationships": {}, "notes": {}
            })
            mark_data.update(qwen_data)
            _save_json(QWEN_MARK_XXX_MEMORY, mark_data)
            log("[Memory] Qwen → JARVIS sync complete")
            return mark_data
    except Exception as e:
        log(f"[Memory] Sync failed: {e}")
    return {}


def get_unified_memory() -> dict:
    """Returns merged memory from both systems."""
    mark_data = _load_json(QWEN_MARK_XXX_MEMORY, {})
    shared = _load_json(SHARED_MEMORY, {})
    qwen_data = shared.get("qwen_memory", {})

    unified = {}
    for key in set(list(mark_data.keys()) + list(qwen_data.keys())):
        if key in mark_data and key in qwen_data:
            # Merge: Qwen data takes precedence for conflicts
            unified[key] = {**mark_data[key], **qwen_data[key]}
        elif key in mark_data:
            unified[key] = mark_data[key]
        else:
            unified[key] = qwen_data[key]

    return unified


# ─── JARVIS Skill API (for Qwen to call directly) ────────────────────────────

class JarvisSkillAPI:
    """
    Direct Python API to JARVIS actions — no voice needed.
    Qwen calls these methods to execute JARVIS capabilities.
    """

    def __init__(self):
        self._actions = {}
        self._load_actions()

    def _load_actions(self):
        """Dynamically import all JARVIS action modules."""
        actions_dir = BASE_DIR / "actions"
        action_map = {
            "open_app": "open_app",
            "web_search": "web_search",
            "weather": "weather_report",
            "send_message": "send_message",
            "reminder": "reminder",
            "youtube": "youtube_video",
            "screen_vision": "screen_processor",
            "computer_settings": "computer_settings",
            "browser": "browser_control",
            "file_manager": "file_controller",
            "cmd": "cmd_control",
            "desktop": "desktop",
            "code_helper": "code_helper",
            "dev_agent": "dev_agent",
            "flight_finder": "flight_finder",
            "computer_control": "computer_control",
        }

        for api_name, module_name in action_map.items():
            try:
                module_path = actions_dir / f"{module_name}.py"
                if module_path.exists():
                    # Import dynamically
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Get the main function
                    func_name = module_name
                    if hasattr(module, func_name):
                        self._actions[api_name] = getattr(module, func_name)
                        log(f"[JarvisSkill] Loaded: {api_name}")
            except Exception as e:
                log(f"[JarvisSkill] Failed to load {api_name}: {e}")

    def execute(self, action: str, params: dict = None) -> Any:
        """Execute a JARVIS action directly."""
        if action not in self._actions:
            return f"Unknown action: {action}. Available: {list(self._actions.keys())}"

        try:
            func = self._actions[action]
            result = func(parameters=params or {}, player=None)
            log(f"[JarvisSkill] ✅ {action} → {str(result)[:100]}")
            return result
        except Exception as e:
            log(f"[JarvisSkill] ❌ {action} failed: {e}")
            return f"Action '{action}' failed: {e}"

    def list_actions(self) -> list:
        """List all available JARVIS actions."""
        return list(self._actions.keys())

    # ─── Convenience Methods ──────────────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        return self.execute("open_app", {"app_name": app_name})

    def search_web(self, query: str) -> str:
        return self.execute("web_search", {"query": query})

    def get_weather(self, city: str) -> str:
        return self.execute("weather", {"city": city})

    def send_message(self, receiver: str, message: str, platform: str = "WhatsApp") -> str:
        return self.execute("send_message", {
            "receiver": receiver, "message_text": message, "platform": platform
        })

    def set_reminder(self, date: str, time: str, message: str) -> str:
        return self.execute("reminder", {
            "date": date, "time": time, "message": message
        })

    def control_browser(self, action: str, **kwargs) -> str:
        params = {"action": action, **kwargs}
        return self.execute("browser", params)

    def manage_files(self, action: str, **kwargs) -> str:
        params = {"action": action, **kwargs}
        return self.execute("file_manager", params)

    def run_command(self, task: str) -> str:
        return self.execute("cmd", {"task": task})

    def control_computer(self, action: str, **kwargs) -> str:
        params = {"action": action, **kwargs}
        return self.execute("computer_control", params)

    def control_settings(self, action: str, **kwargs) -> str:
        params = {"action": action, **kwargs}
        return self.execute("computer_settings", params)

    def manage_desktop(self, action: str, **kwargs) -> str:
        params = {"action": action, **kwargs}
        return self.execute("desktop", params)

    def write_code(self, description: str, language: str = "python") -> str:
        return self.execute("code_helper", {
            "action": "write", "description": description, "language": language
        })

    def build_project(self, description: str, language: str = "python") -> str:
        return self.execute("dev_agent", {
            "description": description, "language": language
        })

    def find_flights(self, origin: str, destination: str, date: str, **kwargs) -> str:
        params = {"origin": origin, "destination": destination, "date": date, **kwargs}
        return self.execute("flight_finder", params)

    def analyze_screen(self, question: str) -> str:
        return self.execute("screen_vision", {"text": question, "angle": "screen"})

    def analyze_camera(self, question: str) -> str:
        return self.execute("screen_vision", {"text": question, "angle": "camera"})


# ─── Background Monitor (JARVIS → Qwen task watcher) ─────────────────────────

class QwenTaskMonitor:
    """
    Runs inside JARVIS's main.py as a background thread.
    Watches for tasks from Qwen and executes them.
    """

    def __init__(self, speak_callback: Callable = None):
        self._running = False
        self._thread = None
        self._speak = speak_callback

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="QwenTaskMonitor"
        )
        self._thread.start()
        log("[Monitor] Qwen task monitor started")

    def stop(self):
        self._running = False
        log("[Monitor] Qwen task monitor stopped")

    def _monitor_loop(self):
        while self._running:
            try:
                tasks = _load_json(TASK_QUEUE, [])
                for task in tasks:
                    if task.get("status") == TaskStatus.PENDING.value:
                        self._execute_task(task)

                # Clean old results (older than 1 hour)
                self._cleanup_old_results()

            except Exception as e:
                log(f"[Monitor] Error: {e}")

            time.sleep(2)

    def _execute_task(self, task: dict):
        task_id = task["task_id"]
        goal = task.get("goal", "")
        action = task.get("action", "execute")
        params = task.get("params", {})

        log(f"[Monitor] Executing: [{task_id}] {action} — {goal[:80]}")

        # Update status
        task["status"] = TaskStatus.RUNNING.value
        _save_json(TASK_QUEUE, _load_json(TASK_QUEUE, []))

        try:
            if action == "speak":
                result = goal
                if self._speak:
                    self._speak(goal)

            elif action == "execute":
                # Use JarvisSkillAPI to execute
                api = JarvisSkillAPI()
                # Determine which action to call from goal
                result = api.execute(goal, params)

            elif action == "vision":
                api = JarvisSkillAPI()
                result = api.analyze_screen(goal)

            else:
                result = f"Unknown action type: {action}"

            # Save result
            self._save_result(task_id, result)

        except Exception as e:
            self._save_result(task_id, None, str(e))

    def _save_result(self, task_id: str, result: Any, error: str = None):
        result_entry = {
            "task_id": task_id,
            "result": str(result) if result else None,
            "error": error,
            "status": TaskStatus.FAILED.value if error else TaskStatus.COMPLETED.value,
            "completed_at": datetime.now().isoformat(),
        }

        results = _load_json(RESULT_QUEUE, [])
        results.append(result_entry)
        _save_json(RESULT_QUEUE, results)

        # Update task status
        tasks = _load_json(TASK_QUEUE, [])
        for t in tasks:
            if t["task_id"] == task_id:
                t["status"] = result_entry["status"]
                t["result"] = result_entry["result"]
                t["error"] = error
                break
        _save_json(TASK_QUEUE, tasks)

        log(f"[Monitor] Result saved: [{task_id}] {result_entry['status']}")

    def _cleanup_old_results(self):
        """Remove results older than 1 hour."""
        try:
            results = _load_json(RESULT_QUEUE, [])
            cutoff = datetime.now().timestamp() - 3600
            results = [
                r for r in results
                if r.get("completed_at") and
                datetime.fromisoformat(r["completed_at"]).timestamp() > cutoff
            ]
            _save_json(RESULT_QUEUE, results)
        except Exception:
            pass


# ─── Utility Functions ────────────────────────────────────────────────────────

def _load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default if default is not None else []


def _save_json(path: Path, data: Any):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"[IO] Save failed: {path}: {e}")


# ─── Main (Test Mode) ────────────────────────────────────────────────────────

def main():
    """Test the bridge system."""
    print("=" * 60)
    print("  JARVIS-QWEN Bridge System Test")
    print("=" * 60)

    # Test 1: Load actions
    print("\n[1] Loading JARVIS actions...")
    api = JarvisSkillAPI()
    actions = api.list_actions()
    print(f"    ✅ {len(actions)} actions loaded: {actions}")

    # Test 2: Submit task
    print("\n[2] Submitting test task...")
    task_id = submit_task("Test task from Qwen", TaskPriority.HIGH)
    print(f"    ✅ Task ID: {task_id}")

    # Test 3: Memory sync
    print("\n[3] Testing memory sync...")
    mark_mem = sync_memory_to_qwen()
    print(f"    ✅ JARVIS memory: {len(mark_mem)} categories")

    unified = get_unified_memory()
    print(f"    ✅ Unified memory: {len(unified)} categories")

    # Test 4: Status
    print("\n[4] Bridge status...")
    status = {
        "bridge": "active",
        "actions_loaded": len(actions),
        "memory_synced": True,
        "timestamp": datetime.now().isoformat(),
    }
    _save_json(STATUS_FILE, status)
    print(f"    ✅ Status saved")

    print("\n" + "=" * 60)
    print("  Bridge system ready for Qwen integration!")
    print("=" * 60)


if __name__ == "__main__":
    main()
