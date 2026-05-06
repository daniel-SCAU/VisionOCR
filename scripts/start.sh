#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-$(pwd)}"
exec uvicorn app.main:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}" "$@"
