#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python -m build_status watch --root .
