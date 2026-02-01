@echo off
setlocal enabledelayedexpansion

python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Virtualenv created at .venv and requirements installed.

