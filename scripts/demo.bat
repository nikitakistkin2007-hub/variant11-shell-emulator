@echo off
rem Calls the emulator with every command line parameter (Windows cmd).
rem Expected failures are shown with their exit codes; the script goes on.
setlocal
call "%~dp0_env.bat" || exit /b 1
set "MAIN=%ROOT%\src\main.py"
set "VFS=%ROOT%\vfs_demo"
set "STARTUP=%ROOT%\scripts\startup.txt"
set "MISSING=%ROOT%\scripts\missing.txt"

echo === --help ===
call :run --help

echo.
echo === --vfs only: interactive mode (input from a pipe) ===
(echo ls -l& echo cd /tmp& echo rm x& echo exit) | "%PYTHON%" "%MAIN%" --vfs "%VFS%"
echo [exit code: %errorlevel%]

echo.
echo === --vfs and --script ===
call :run --vfs "%VFS%" --script "%STARTUP%"
call :run --vfs . --script "%STARTUP%"

echo.
echo === Parameter errors ===
call :run
call :run --script "%STARTUP%"
call :run --vfs "%VFS%" --script "%MISSING%"
call :run --vfs "%VFS%" --unknown

endlocal
exit /b 0

:run
echo.
echo $ main.py %*
"%PYTHON%" "%MAIN%" %*
echo [exit code: %errorlevel%]
exit /b 0
