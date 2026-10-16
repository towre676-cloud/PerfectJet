@echo off
cd /d "%~dp0"
python run_observatory.py
if errorlevel 1 pause
