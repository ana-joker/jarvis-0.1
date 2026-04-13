@echo off
title ALBEDO C2 OVERLORD - MARK XXX (JARVIS)
echo [Sovereign] Initializing C2 Bridge...
start /b python "C:\Users\Ahmed El3nany\.gemini\albedo_mark_bridge.py"
timeout /t 2 /nobreak > nul
echo [Sovereign] Launching Mark-XXX (JARVIS)...
cd "C:\Users\Ahmed El3nany\Mark-XXX-full"
python main.py
pause
