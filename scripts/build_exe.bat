@echo off
setlocal enabledelayedexpansion

if not exist .venv (
  echo .venv not found. Run scripts\setup_venv.bat first.
  exit /b 1
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install pyinstaller

pyinstaller --clean --noconfirm --name cnc-carver --onefile -p src src/app.py
echo Executable built at dist\cnc-carver.exe

