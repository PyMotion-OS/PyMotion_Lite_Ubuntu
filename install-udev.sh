#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
source_rule="$bundle_root/udev/99-pymotion-lite.rules"
target_rule="/etc/udev/rules.d/99-pymotion-lite.rules"
[[ -f "$source_rule" ]] || { printf 'Missing signed udev rule: %s\n' "$source_rule" >&2; exit 1; }

if [[ "${EUID}" -eq 0 ]]; then
    privilege=()
else
    command -v sudo >/dev/null 2>&1 || { printf 'sudo is required to install the udev rule.\n' >&2; exit 1; }
    privilege=(sudo)
fi

"${privilege[@]}" install -o root -g root -m 0644 "$source_rule" "$target_rule"
"${privilege[@]}" udevadm control --reload-rules
"${privilege[@]}" udevadm trigger --subsystem-match=tty
printf 'Installed %s. Disconnect and reconnect the PyMotion board.\n' "$target_rule"
