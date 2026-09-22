@echo off
setlocal
cd /d "%~dp0\.."
py -3 scripts\checkpoint.py %* 2>nul || python scripts\checkpoint.py %*
