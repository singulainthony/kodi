#!/usr/bin/env bash
# Build LeanFlix repository + wizard zips.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/package.py"
