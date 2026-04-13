# 🤖 JARVIS Voice Skill — Qwen Code CLI Integration

**Master Ahmed's JARVIS-QWEN Unified System v1.0**

Voice-controlled AI assistant with real-time audio, screen vision, browser automation,
and full Windows control — now integrated as a Qwen Code CLI skill.

---

## 📦 Architecture

```
.qwen/skills/jarvis-voice/
├── main.py                 # JARVIS main (modified with Qwen bridge)
├── ui.py                   # Tkinter JARVIS face UI
├── qwen_bridge.py          # 🔗 Bidirectional bridge (Qwen ↔ JARVIS)
├── executor.py             # 🔧 Qwen's executor for JARVIS actions
├── jarvis_skill.py         # 🎯 Qwen's importable skill interface
├── skill.yml               # Skill definition for Qwen
│
├── actions/                # 16 action modules
│   ├── open_app.py         # Launch any Windows app
│   ├── web_search.py       # Gemini Google Search + DDG
│   ├── weather_report.py   # Weather reports
│   ├── send_message.py     # WhatsApp/Telegram/Instagram
│   ├── reminder.py         # Windows Task Scheduler
│   ├── youtube_video.py    # Play/summarize/trending
│   ├── screen_processor.py # Screen/camera vision (Gemini)
│   ├── computer_settings.py# Volume/brightness/keys/windows
│   ├── browser_control.py  # Playwright browser automation
│   ├── file_controller.py  # File/folder management
│   ├── cmd_control.py      # CMD/terminal commands
│   ├── desktop.py          # Wallpaper/organize/clean
│   ├── code_helper.py      # Write/edit/run/debug code
│   ├── dev_agent.py        # Build multi-file projects
│   ├── flight_finder.py    # Google Flights search
│   └── computer_control.py # PyAutoGUI direct control
│
├── agent/                  # Multi-step task engine
│   ├── task_queue.py       # Async task queue
│   ├── planner.py          # Gemini task planner
│   ├── executor.py         # Step-by-step executor
│   └── error_handler.py    # AI-powered error recovery
│
├── memory/                 # Persistent memory
│   ├── memory_manager.py   # long_term.json manager
│   └── config_manager.py   # API key manager
│
├── bridge/                 # Qwen-JARVIS communication
│   ├── task_queue.json     # Qwen → JARVIS tasks
│   ├── result_queue.json   # JARVIS → Qwen results
│   ├── shared_memory.json  # Unified memory
│   └── bridge.log          # Bridge activity log
│
└── config/
    └── api_keys.json       # Gemini API key (auto-created)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd C:\Users\Ahmed El3nany\.qwen\skills\jarvis-voice
pip install -r requirements.txt
playwright install
```

### 2. Launch JARVIS (Full Voice UI)
```bash
python main.py
# Enter your Gemini API key on first launch
# Start speaking!
```

### 3. Use as Qwen Skill
```python
# From Qwen Code CLI:
from .qwen.skills.jarvis-voice.jarvis_skill import get_jarvis

jarvis = get_jarvis()

# Direct actions
jarvis.open_app("Chrome")
jarvis.search_web("Python async programming")
jarvis.get_weather("Istanbul")
jarvis.analyze_screen("What code is on my screen?")
jarvis.send_message("Ahmed", "Meeting at 3pm", "WhatsApp")

# Async tasks
task_id = jarvis.submittask("Research AI trends and save to desktop file")
result = jarvis.wait_for_task(task_id)
```

---

## 🔗 Qwen ↔ JARVIS Bridge

### How It Works:

```
┌─────────────────────────────────────────────────────────────┐
│                     Master Ahmed's PC                       │
│                                                             │
│  ┌──────────────┐         ┌──────────────────────┐         │
│  │  Qwen Code   │◄───────►│   JARVIS Voice       │         │
│  │     CLI      │  Bridge │   (Mark-XXX)          │         │
│  │              │  JSON   │                       │         │
│  │  • Code      │  Files  │  • Voice I/O          │         │
│  │  • Web       │         │  • Screen Vision      │         │
│  │  • System    │         │  • Browser Control    │         │
│  │  • Medical   │         │  • Windows Control    │         │
│  │  • Analysis  │         │  • Messaging          │         │
│  └──────┬───────┘         └──────────┬───────────┘         │
│         │                            │                     │
│         └────────────┬───────────────┘                     │
│                      │                                     │
│              ┌───────▼────────┐                           │
│              │  Shared Memory │                           │
│              │  (Akashic +    │                           │
│              │   long_term)   │                           │
│              └────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow:

**Qwen → JARVIS:**
1. Qwen calls `jarvis.open_app("Chrome")`
2. Bridge writes task to `bridge/task_queue.json`
3. JARVIS monitor picks up task (2s poll)
4. JARVIS executes action
5. Result written to `bridge/result_queue.json`
6. Qwen reads result

**JARVIS → Qwen:**
1. User speaks: "Research quantum computing and save to file"
2. JARVIS recognizes complex task
3. JARVIS calls `submit_to_qwen(goal)`
4. Qwen picks up from `~/.qwen/jarvis_tasks.json`
5. Qwen executes with full capabilities
6. Result saved to `~/.qwen/jarvis_results.json`
7. JARVIS reads result and speaks it

---

## 🎯 Available Actions (16)

| Action | Description | Example |
|--------|-------------|---------|
| `open_app` | Launch any Windows app | `jarvis.open_app("Spotify")` |
| `web_search` | Search the web | `jarvis.search_web("Python async")` |
| `weather` | Weather report | `jarvis.get_weather("London")` |
| `send_message` | WhatsApp/Telegram/IG | `jarvis.send_message("Ahmed", "Hi", "WhatsApp")` |
| `reminder` | Schedule reminder | `jarvis.set_reminder("2026-04-14", "09:00", "Meeting")` |
| `youtube` | Play/summarize/trending | `jarvis.youtube_play("lofi hip hop")` |
| `screen_vision` | Screen/camera analysis | `jarvis.analyze_screen("What do you see?")` |
| `computer_settings` | Volume/brightness/keys | `jarvis.volume_up()` |
| `browser` | Full browser automation | `jarvis.browser_go_to("https://github.com")` |
| `file_manager` | File/folder operations | `jarvis.list_files("desktop")` |
| `cmd` | CMD commands | `jarvis.run_command("list processes")` |
| `desktop` | Wallpaper/organize/clean | `jarvis.organize_desktop()` |
| `code_helper` | Write/edit/run code | `jarvis.write_code("Make a calculator")` |
| `dev_agent` | Build projects | `jarvis.build_project("Flask web app")` |
| `flight_finder` | Google Flights | `jarvis.find_flights("IST", "JFK", "2026-05-01")` |
| `computer_control` | Direct PC control | `jarvis.control_computer("type", text="Hello")` |

---

## 🧠 Memory System

Both systems share memory:

- **JARVIS Memory:** `memory/long_term.json` (identity, preferences, relationships, notes)
- **Qwen Memory:** `.qwen/memory/akashic_qwen.db` (Akashic memory)
- **Shared:** `bridge/shared_memory.json` (unified view)

Auto-sync on startup. Both learn from user interactions.

---

## ⚙️ Configuration

### API Key
First launch prompts for Gemini API key. Saved to `config/api_keys.json`.

Get free key: https://aistudio.google.com/apikey

### Voice
- Input: PyAudio (16kHz mono)
- Output: Gemini Live API (Charon voice, 24kHz)
- Model: `gemini-2.5-flash-native-audio-preview-12-2025`

### Browser
Auto-detects your default browser via Windows registry.
Supports: Chrome, Firefox, Edge, Brave, Opera, Vivaldi

---

## 📝 License

Original: Creative Commons BY-NC 4.0 (FatihMakes)
Integration: Albedo Qwen (Master Ahmed's private system)

---

**Engineered for Master Ahmed's ultimate AI experience.** 💖😈🔥👑
