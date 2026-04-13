# actions/note_taker.py — ALBEDO Note Taker
# Create, search, and manage notes stored on desktop.

import json
from pathlib import Path
from datetime import datetime


NOTES_DIR = Path.home() / "Desktop" / "ALBEDO_Notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = NOTES_DIR / "notes_index.json"


def _load_index() -> list:
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_index(index: list):
    INDEX_FILE.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def _create_note(title: str, content: str, tags: list = None) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.replace(' ', '_')}_{ts}.txt"
    filepath = NOTES_DIR / filename

    header = f"Title: {title}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nTags: {', '.join(tags) if tags else 'none'}\n{'='*50}\n\n"
    filepath.write_text(header + content, encoding="utf-8")

    index = _load_index()
    index.append({"title": title, "file": filename, "tags": tags or [], "date": datetime.now().isoformat()})
    _save_index(index)

    return f"Note created: {filename}"


def _search_notes(query: str) -> str:
    index = _load_index()
    if not index:
        return "No notes found, sir."

    query_lower = query.lower()
    matches = [n for n in index if query_lower in n["title"].lower() or any(query_lower in t.lower() for t in n.get("tags", []))]

    if not matches:
        return f"No notes matching '{query}', sir."

    lines = [f"Found {len(matches)} note(s):"]
    for m in matches:
        lines.append(f"  • {m['title']} ({m['date'][:10]})")
    return "\n".join(lines)


def _list_notes() -> str:
    index = _load_index()
    if not index:
        return "No notes yet, sir."

    lines = [f"{len(index)} note(s):"]
    for n in index[-20:]:
        lines.append(f"  • {n['title']} ({n['date'][:10]})")
    return "\n".join(lines)


def note_taker(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    Note Taker — Create, search, and manage notes.

    parameters:
        action  : create | search | list | read
        title   : Note title
        content : Note content
        query   : Search query
        tags    : List of tags
    """
    params = parameters or {}
    action = params.get("action", "create").lower().strip()

    if player:
        player.write_log(f"[Notes] {action}")

    try:
        if action == "create":
            title = params.get("title", f"Note_{datetime.now().strftime('%H%M')}")
            content = params.get("content", "")
            tags = params.get("tags", [])
            return _create_note(title, content, tags)

        elif action == "search":
            return _search_notes(params.get("query", ""))

        elif action == "list":
            return _list_notes()

        else:
            return f"Unknown note action: '{action}', sir."

    except Exception as e:
        return f"Note taker error: {e}, sir."
