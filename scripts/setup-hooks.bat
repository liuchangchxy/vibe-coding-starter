@echo off
setlocal
cd /d "%~dp0\.."
py -3 scripts\setup-hooks.py %* 2>nul || python scripts\setup-hooks.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Hook installation failed.
    pause
) else (
    echo.
    echo [SUCCESS] Git pre-commit hook is now active!
)
pause
