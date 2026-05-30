@echo off
title JARVIS SERVER
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause