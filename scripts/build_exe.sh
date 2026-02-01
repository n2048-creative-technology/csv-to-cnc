#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup_venv.sh first." >&2
  exit 1
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install pyinstaller

pyinstaller \
  --clean \
  --noconfirm \
  --name cnc-carver \
  --onefile \
  -p src \
  src/app.py

echo "Executable built at dist/cnc-carver"

