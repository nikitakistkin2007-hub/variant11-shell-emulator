@echo off
rem Runs all unit tests.
setlocal
call "%~dp0_env.bat" || exit /b 1

cd /d "%ROOT%"
"%PYTHON%" -m unittest discover -s tests -v
endlocal
