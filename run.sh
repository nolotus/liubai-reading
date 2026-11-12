#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 -c 'import fitz' 2>/dev/null || { echo '请先运行：python3 -m pip install -r requirements.txt'; exit 1; }
exec python3 app.py
