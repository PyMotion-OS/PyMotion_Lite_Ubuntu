#!/usr/bin/env bash
set -euo pipefail

target_rule="/etc/udev/rules.d/99-pymotion-lite.rules"
if [[ "${EUID}" -eq 0 ]]; then
    privilege=()
else
    command -v sudo >/dev/null 2>&1 || { printf 'sudo is required to remove the udev rule.\n' >&2; exit 1; }
    privilege=(sudo)
fi

if [[ -f "$target_rule" ]]; then
    "${privilege[@]}" rm -f -- "$target_rule"
    "${privilege[@]}" udevadm control --reload-rules
    "${privilege[@]}" udevadm trigger --subsystem-match=tty
    printf 'Removed %s.\n' "$target_rule"
else
    printf 'PyMotion udev rule is not installed.\n'
fi
