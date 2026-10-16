@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 run_observatory.py
) else (
  python run_observatory.py
)
if errorlevel 1 (
  echo.
  echo Python 3.10 or newer is required. See docs/OBSERVATORY.md.
  pause
)
endlocal
