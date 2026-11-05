#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ge 2 ]] || { printf 'Usage: %s SDK_PYTHON SCRIPT [ARGUMENT ...]\n' "$0" >&2; exit 2; }
sdk_python="$1"
shift
[[ -x "$sdk_python" ]] || { printf 'PyMotion Lite SDK Python was not found: %s\n' "$sdk_python" >&2; exit 2; }

exec "$sdk_python" -u "$@"
