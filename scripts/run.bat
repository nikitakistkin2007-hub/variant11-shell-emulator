@echo off
rem Starts the emulator in interactive mode on the demo VFS.
rem Optional: run.bat path\to\script.txt  - run a startup script instead.
setlocal
call "%~dp0_env.bat" || exit /b 1

if "%~1"=="" (
    "%PYTHON%" "%ROOT%\src\main.py" --vfs "%ROOT%\vfs_demo"
) else (
    "%PYTHON%" "%ROOT%\src\main.py" --vfs "%ROOT%\vfs_demo" --script "%~1"
)
endlocal
