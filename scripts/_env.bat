@echo off
rem Helper for the other scripts: sets ROOT and finds a working Python.
rem Use PYTHON=... (set before running) to force a specific interpreter.
set "ROOT=%~dp0.."
if not defined PYTHON (
    py --version >nul 2>nul && set "PYTHON=py"
)
if not defined PYTHON (
    python --version >nul 2>nul && set "PYTHON=python"
)
if not defined PYTHON (
    echo [error] Python was not found.
    echo Install Python 3.10+ from https://www.python.org/downloads/
    echo and tick "Add python.exe to PATH" in the installer.
    pause
    exit /b 1
)
exit /b 0
