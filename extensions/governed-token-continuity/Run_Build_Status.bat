@echo off
setlocal
cd /d "%~dp0"
python -m build_status watch --root .
endlocal
