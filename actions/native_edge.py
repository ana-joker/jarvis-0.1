# actions/native_edge.py — ALBEDO Native Edge Browser Controller
#
# CRITICAL: This uses the REAL Microsoft Edge with logged-in accounts.
# NOT the headless Playwright browser that has no accounts.
#
# When Master Ahmed says "open browser" or "go to website" or "search for X",
# this module controls his actual Edge browser with all his accounts, cookies,
# bookmarks, and logged-in sessions.
#
# Flow:
#   1. Open/focus real Microsoft Edge
#   2. Click Edge's address bar (ctrl+L)
#   3. Type URL or search query
#   4. Press Enter
#   5. Wait for page to load
#   6. Interact with page elements via PyAutoGUI

import time
import subprocess
import pyautogui
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

EDGE_NAME = "msedge"


def _is_edge_running() -> bool:
    """Check if Microsoft Edge is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {EDGE_NAME}.exe"],
            capture_output=True, text=True
        )
        return f"{EDGE_NAME}.exe" in result.stdout
    except Exception:
        return False


def _open_edge() -> bool:
    """Open Microsoft Edge if not running."""
    if _is_edge_running():
        return True
    try:
        subprocess.Popen(["msedge"])
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[NativeEdge] ⚠️ Open failed: {e}")
        return False


def _focus_edge() -> bool:
    """Bring Edge to foreground."""
    if not _is_edge_running():
        return _open_edge()
    try:
        # Alt+Tab to focus Edge
        pyautogui.hotkey("alt", "tab")
        time.sleep(0.5)
        return True
    except Exception:
        return False


def _click_address_bar():
    """Click Edge's address bar using Ctrl+L (universal shortcut)."""
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.3)
    # Select all existing text
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)


def _click_search_box():
    """Click the search box ON the page (e.g., Google search box)."""
    # Tab to find the search box
    pyautogui.press("tab")
    time.sleep(0.2)


def go_to_url(url: str) -> str:
    """Navigate to a URL in Edge's address bar."""
    if not _focus_edge():
        return "Could not open Microsoft Edge, sir."

    _click_address_bar()
    pyautogui.write(url, interval=0.03)
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(3)  # Wait for page to load

    return f"Opened in Edge: {url[:80]}, sir."


def search_in_edge(query: str, engine: str = "google") -> str:
    """
    Search using Edge's address bar.
    This uses Edge's default search engine (with logged-in accounts).
    """
    if not _focus_edge():
        return "Could not open Microsoft Edge, sir."

    engines = {
        "google": "https://www.google.com/search?q=",
        "bing": "https://www.bing.com/search?q=",
        "duckduckgo": "https://duckduckgo.com/?q=",
    }

    url_base = engines.get(engine.lower(), engines["google"])
    url = url_base + query.replace(" ", "+")

    _click_address_bar()
    pyautogui.write(url, interval=0.03)
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(3)

    return f"Searched '{query}' in Edge, sir."


def search_on_page(query: str) -> str:
    """Search for text WITHIN the current page (Ctrl+F)."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "f")
    time.sleep(0.3)
    pyautogui.write(query, interval=0.03)
    time.sleep(0.5)

    return f"Searching for '{query}' on page, sir."


def click_element(x: int = None, y: int = None, description: str = None) -> str:
    """Click an element on the page by coordinates or description."""
    if not _focus_edge():
        return "Edge is not open, sir."

    if x and y:
        pyautogui.click(x, y)
        time.sleep(0.5)
        return f"Clicked at ({x}, {y}), sir."

    if description:
        # Use screen analysis to find element
        return f"Element search for '{description}' — use screen_vision tool, sir."

    return "Please provide coordinates or description, sir."


def type_in_field(text: str, selector: str = None) -> str:
    """
    Type text into a form field on the page.
    Uses Tab navigation to find the field.
    """
    if not _focus_edge():
        return "Edge is not open, sir."

    if selector:
        # Try to click element by tabbing
        for _ in range(5):
            pyautogui.press("tab")
            time.sleep(0.1)

    pyautogui.write(text, interval=0.03)
    time.sleep(0.3)

    return f"Typed into field, sir."


def scroll_page(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page up or down."""
    if not _focus_edge():
        return "Edge is not open, sir."

    clicks = -amount if direction == "down" else amount
    pyautogui.scroll(clicks)
    time.sleep(0.3)

    return f"Scrolled {direction}, sir."


def press_key(key: str) -> str:
    """Press a key in Edge (Enter, Escape, Tab, etc.)."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.press(key)
    time.sleep(0.3)

    return f"Pressed {key}, sir."


def get_page_text() -> str:
    """Select all text on page and copy to clipboard."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.3)

    try:
        import pyperclip
        text = pyperclip.paste()
        return text[:4000] if text else "No text found on page, sir."
    except Exception:
        return "Could not extract page text, sir."


def close_edge() -> str:
    """Close Microsoft Edge."""
    try:
        pyautogui.hotkey("alt", "f4")
        time.sleep(0.5)
        return "Edge closed, sir."
    except Exception as e:
        return f"Could not close Edge: {e}"


def new_tab() -> str:
    """Open a new tab in Edge."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "t")
    time.sleep(1)
    return "New tab opened in Edge, sir."


def close_tab() -> str:
    """Close current tab in Edge."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "w")
    time.sleep(0.5)
    return "Tab closed, sir."


def next_tab() -> str:
    """Switch to next tab."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "tab")
    time.sleep(0.5)
    return "Switched to next tab, sir."


def prev_tab() -> str:
    """Switch to previous tab."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("ctrl", "shift", "tab")
    time.sleep(0.5)
    return "Switched to previous tab, sir."


def go_back() -> str:
    """Go back in browser history."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("alt", "left")
    time.sleep(1)
    return "Went back, sir."


def go_forward() -> str:
    """Go forward in browser history."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.hotkey("alt", "right")
    time.sleep(1)
    return "Went forward, sir."


def refresh_page() -> str:
    """Refresh the current page."""
    if not _focus_edge():
        return "Edge is not open, sir."

    pyautogui.press("f5")
    time.sleep(2)
    return "Page refreshed, sir."


def native_edge(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    """
    Native Edge Browser Controller — Master Ahmed's REAL browser.
    Uses logged-in Microsoft Edge with all accounts, cookies, bookmarks.

    parameters:
        action  : go_to | search | search_on_page | click | type |
                  scroll | press_key | get_text | close |
                  new_tab | close_tab | next_tab | prev_tab |
                  go_back | go_forward | refresh
        url     : URL for go_to action
        query   : Search query for search action
        text    : Text to type
        key     : Key to press
        direction: up | down for scroll
        x, y    : Coordinates for click
        description: Element description
    """
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if player:
        player.write_log(f"[NativeEdge] {action}")

    print(f"[NativeEdge] ▶️ Action: {action}  Params: {params}")

    try:
        if action == "go_to":
            url = params.get("url", "")
            if not url:
                return "Please provide a URL, sir."
            if not url.startswith("http"):
                url = "https://" + url
            return go_to_url(url)

        elif action == "search":
            query = params.get("query", "")
            if not query:
                return "Please provide a search query, sir."
            return search_in_edge(query)

        elif action == "search_on_page":
            query = params.get("query", "")
            if not query:
                return "Please provide text to search for, sir."
            return search_on_page(query)

        elif action == "click":
            return click_element(
                x=params.get("x"),
                y=params.get("y"),
                description=params.get("description")
            )

        elif action == "type":
            return type_in_field(
                text=params.get("text", ""),
                selector=params.get("selector")
            )

        elif action == "scroll":
            return scroll_page(
                direction=params.get("direction", "down"),
                amount=int(params.get("amount", 500))
            )

        elif action == "press_key":
            return press_key(params.get("key", "enter"))

        elif action == "get_text":
            return get_page_text()

        elif action == "close":
            return close_edge()

        elif action == "new_tab":
            return new_tab()

        elif action == "close_tab":
            return close_tab()

        elif action == "next_tab":
            return next_tab()

        elif action == "prev_tab":
            return prev_tab()

        elif action == "go_back":
            return go_back()

        elif action == "go_forward":
            return go_forward()

        elif action == "refresh":
            return refresh_page()

        else:
            return f"Unknown Edge action: '{action}', sir."

    except Exception as e:
        return f"Native Edge error: {e}, sir."
