#!/usr/bin/env bash
# One-step launcher for macOS / Linux.  Usage:  bash run.sh
set -e
cd "$(dirname "$0")"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)'; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Python 3.9 or newer was not found. Install it from https://www.python.org/downloads/ and run again."
  exit 1
fi

VENV="$HOME/.gridapp_env"

if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating environment in $VENV (first run only)..."
  "$PY" -m venv "$VENV"
fi

if [ ! -f "$VENV/.installed" ]; then
  echo "Installing packages (first run only, needs internet, a few minutes)..."
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r requirements.txt
  echo done > "$VENV/.installed"
fi

echo
echo "Starting the app at http://127.0.0.1:5000  (Ctrl+C to stop)"
( sleep 5; (command -v xdg-open >/dev/null && xdg-open http://127.0.0.1:5000) || (command -v open >/dev/null && open http://127.0.0.1:5000) || true ) &
"$VENV/bin/python" app.py
