# actions/send_message.py — ALBEDO Messaging (FIXED v2.0)
#
# CRITICAL FIX: Search bar ≠ Chat box
# - Search bar: TOP-LEFT corner — ONLY used to FIND a conversation
# - Chat box: BOTTOM of screen — ONLY used to TYPE messages
#
# Flow for ALL platforms:
#   1. Open app
#   2. Click search bar (top-left) → search contact name
#   3. Press Enter → OPEN the conversation
#   4. WAIT for chat to load
#   5. Click chat input box (BOTTOM of screen)
#   6. Type message in chat box (NOT search bar!)
#   7. Press Enter to send
#
# NEVER write the message in the search bar. NEVER.

import time
import pyautogui
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.08

# ─── Screen Position Constants (relative) ─────────────────────────────────────
# Search bar: top-left area (~5% from top, ~15% from left)
# Chat box: bottom-center area (~85% from top, ~50% from left)

SEARCH_BAR_RATIO = (0.05, 0.15)   # (y_ratio, x_ratio)
CHAT_BOX_RATIO   = (0.85, 0.50)   # (y_ratio, x_ratio)


def _get_screen_pos(ratio: tuple) -> tuple:
    """Convert screen ratio to actual pixel coordinates."""
    w, h = pyautogui.size()
    return (int(w * ratio[1]), int(h * ratio[0]))


def _open_app(app_name: str) -> bool:
    """Opens an app via Windows search."""
    try:
        pyautogui.press("win")
        time.sleep(0.4)
        pyautogui.write(app_name, interval=0.04)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(2.5)  # Wait for app to fully load
        return True
    except Exception as e:
        print(f"[SendMessage] Could not open {app_name}: {e}")
        return False


def _click_search_bar():
    """Click the search bar (top-left area) to search for a contact."""
    x, y = _get_screen_pos(SEARCH_BAR_RATIO)
    pyautogui.click(x, y)
    time.sleep(0.3)
    # Select all existing text in search bar
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)


def _click_chat_box():
    """Click the chat input box (bottom-center) to type a message."""
    x, y = _get_screen_pos(CHAT_BOX_RATIO)
    pyautogui.click(x, y)
    time.sleep(0.3)
    # Clear any existing text
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    time.sleep(0.1)


def _search_contact(contact: str):
    """
    Search for a contact in the search bar.
    MUST be done BEFORE typing any message.
    """
    _click_search_bar()
    pyautogui.write(contact, interval=0.04)
    time.sleep(1.0)  # Wait for search results


def _open_conversation():
    """
    After searching, press Enter to OPEN the first search result.
    This navigates INTO the conversation.
    """
    pyautogui.press("enter")
    time.sleep(1.5)  # Wait for conversation to load


def _type_message(message: str):
    """
    Type the message in the CHAT BOX (bottom of screen).
    NEVER in the search bar.
    """
    _click_chat_box()
    pyautogui.write(message, interval=0.03)
    time.sleep(0.2)


def _send_message():
    """Press Enter to send the message."""
    pyautogui.press("enter")
    time.sleep(0.3)


def _send_whatsapp(receiver: str, message: str) -> str:
    """
    FIXED WhatsApp flow:
    1. Open WhatsApp
    2. Click SEARCH BAR → search contact
    3. Press Enter → OPEN conversation
    4. Click CHAT BOX → type message
    5. Press Enter → send
    """
    try:
        if not _open_app("WhatsApp"):
            return "Could not open WhatsApp, sir."

        time.sleep(1.5)

        # STEP 1: Search for contact (search bar - top-left)
        print(f"[SendMessage] 🔍 Searching for: {receiver}")
        _search_contact(receiver)

        # STEP 2: Open conversation
        print(f"[SendMessage] 📂 Opening conversation with: {receiver}")
        _open_conversation()

        # STEP 3: Type message in CHAT BOX (bottom - NOT search bar!)
        print(f"[SendMessage] ✍️ Typing message in chat box...")
        _type_message(message)

        # STEP 4: Send
        print(f"[SendMessage] 📤 Sending...")
        _send_message()

        return f"Message sent to {receiver} via WhatsApp, sir."

    except Exception as e:
        return f"WhatsApp error: {e}"


def _send_telegram(receiver: str, message: str) -> str:
    """
    FIXED Telegram flow:
    Same as WhatsApp — search bar ≠ chat box
    """
    try:
        if not _open_app("Telegram"):
            return "Could not open Telegram, sir."

        time.sleep(1.5)

        # STEP 1: Search for contact (search bar - top-left)
        print(f"[SendMessage] 🔍 Searching for: {receiver}")
        _search_contact(receiver)

        # STEP 2: Open conversation
        print(f"[SendMessage] 📂 Opening conversation with: {receiver}")
        _open_conversation()

        # STEP 3: Type message in CHAT BOX (bottom - NOT search bar!)
        print(f"[SendMessage] ✍️ Typing message in chat box...")
        _type_message(message)

        # STEP 4: Send
        print(f"[SendMessage] 📤 Sending...")
        _send_message()

        return f"Message sent to {receiver} via Telegram, sir."

    except Exception as e:
        return f"Telegram error: {e}"


def _send_instagram(receiver: str, message: str) -> str:
    """
    Instagram DM via browser.
    Flow: Open Instagram direct → search → select → type in chat box → send
    """
    try:
        import webbrowser

        # Open Instagram direct messages
        webbrowser.open("https://www.instagram.com/direct/inbox/")
        time.sleep(4.0)

        # STEP 1: Search for contact (search bar)
        print(f"[SendMessage] 🔍 Searching for: {receiver}")
        _search_contact(receiver)

        # STEP 2: Open conversation
        print(f"[SendMessage] 📂 Opening conversation with: {receiver}")
        _open_conversation()
        time.sleep(1.0)

        # STEP 3: Type message in CHAT BOX
        print(f"[SendMessage] ✍️ Typing message in chat box...")
        _type_message(message)

        # STEP 4: Send
        print(f"[SendMessage] 📤 Sending...")
        _send_message()

        return f"Message sent to {receiver} via Instagram, sir."

    except Exception as e:
        return f"Instagram error: {e}"


def _send_generic(platform: str, receiver: str, message: str) -> str:
    """
    Generic messaging flow for any app.
    Always: search bar → open conversation → chat box → send
    """
    try:
        if not _open_app(platform):
            return f"Could not open {platform}, sir."

        time.sleep(1.5)

        # STEP 1: Search for contact
        _search_contact(receiver)

        # STEP 2: Open conversation
        _open_conversation()

        # STEP 3: Type in chat box
        _type_message(message)

        # STEP 4: Send
        _send_message()

        return f"Message sent to {receiver} via {platform}, sir."

    except Exception as e:
        return f"{platform} error: {e}"


def send_message(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None
) -> str:
    """
    Called from main.py.

    parameters:
        receiver     : Contact name to send to
        message_text : The message content
        platform     : whatsapp | instagram | telegram | <any app name>
                       Default: whatsapp
    """
    params       = parameters or {}
    receiver     = params.get("receiver", "").strip()
    message_text = params.get("message_text", "").strip()
    platform     = params.get("platform", "whatsapp").strip().lower()

    if not receiver:
        return "Please specify who to send the message to, sir."
    if not message_text:
        return "Please specify what message to send, sir."

    print(f"[SendMessage] 📨 {platform} → {receiver}: {message_text[:40]}")
    if player:
        player.write_log(f"[msg] Sending to {receiver} via {platform}...")

    if "whatsapp" in platform or "wp" in platform or "wapp" in platform:
        result = _send_whatsapp(receiver, message_text)

    elif "instagram" in platform or "ig" in platform or "insta" in platform:
        result = _send_instagram(receiver, message_text)

    elif "telegram" in platform or "tg" in platform:
        result = _send_telegram(receiver, message_text)

    else:
        result = _send_generic(platform, receiver, message_text)

    print(f"[SendMessage] ✅ {result}")
    if player:
        player.write_log(f"[msg] {result}")

    return result
