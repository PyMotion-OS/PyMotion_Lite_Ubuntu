#!/usr/bin/env bash
set -euo pipefail

script_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
bundle_root="$script_root"
payload_root="$script_root"
content_root="$script_root"
python_command="${PYMOTION_PYTHON:-python3}"
data_root="${XDG_DATA_HOME:-${HOME}/.local/share}"
compact_layout=0
if [[ -f "$script_root/RELEASE-MANIFEST.json" && -f "$script_root/../setup-ubuntu.sh" ]]; then
    if "$python_command" -c 'import json,sys; raise SystemExit(0 if json.load(open(sys.argv[1], encoding="utf-8")).get("install_policy", {}).get("compact_layout") is True else 1)' "$script_root/RELEASE-MANIFEST.json"; then
        compact_layout=1
        bundle_root="$(CDPATH= cd -- "$script_root/.." && pwd -P)"
        content_root="$bundle_root"
    fi
fi

bash "$payload_root/verify.sh"

if [[ "$compact_layout" -eq 1 ]]; then
    python_tag="unrestricted"
    python_version="selected interpreter"
    venv_path="${PYMOTION_VENV:-${data_root}/pymotion-lite/venv-ubuntu}"
else
    "$python_command" -c 'import platform, sys; assert platform.python_implementation() == "CPython" and (3, 10) <= sys.version_info < (3, 15)' \
        || { printf 'PyMotion Lite requires CPython 3.10 through 3.14.\n' >&2; exit 1; }
    python_tag="$("$python_command" -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')"
    python_version="$("$python_command" -c 'import platform; print(platform.python_version())')"
    venv_path="${PYMOTION_VENV:-${data_root}/pymotion-lite/venv-${python_tag}}"
fi

venv_python="$venv_path/bin/python"
venv_has_pip() {
    [[ -x "$venv_python" ]] \
        && "$venv_python" -m pip --version >/dev/null 2>&1
}

backup_incomplete_venv() {
    [[ -e "$venv_path" ]] || return 0
    if [[ ! -f "$venv_path/pyvenv.cfg" && ! -x "$venv_python" ]]; then
        if find "$venv_path" -mindepth 1 -print -quit 2>/dev/null | grep -q .; then
            printf 'Installation directory exists but is not a Python virtual environment: %s\n' "$venv_path" >&2
            exit 1
        fi
        return 0
    fi
    backup_path="${venv_path}.broken-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    printf 'Existing incomplete Python environment has no working pip.\n' >&2
    printf 'Moving it to: %s\n' "$backup_path" >&2
    mv -- "$venv_path" "$backup_path"
}

install_ubuntu_venv_support() {
    [[ -r /etc/os-release ]] || return 1
    # shellcheck disable=SC1091
    source /etc/os-release
    [[ "${ID:-}" == "ubuntu" && "${VERSION_ID:-}" =~ ^(22\.04|24\.04)$ ]] \
        || return 1
    command -v apt-get >/dev/null 2>&1 || return 1
    command -v sudo >/dev/null 2>&1 || return 1
    printf '%s\n' 'Python venv support is missing; installing Ubuntu package python3-venv.' >&2
    sudo apt-get update
    sudo apt-get install -y python3-venv
}

install_debian_venv_support() {
    [[ -r /etc/os-release ]] || return 1
    # shellcheck disable=SC1091
    source /etc/os-release
    [[ "${ID:-}" == "debian" && "${VERSION_ID:-}" == "13" ]] || return 1
    command -v apt-get >/dev/null 2>&1 || return 1
    command -v sudo >/dev/null 2>&1 || return 1
    printf '%s\n' 'Python venv support is missing; installing Debian package python3.13-venv.' >&2
    sudo apt-get update
    sudo apt-get install -y python3.13-venv
}

if ! venv_has_pip; then
    backup_incomplete_venv
    mkdir -p "$(dirname -- "$venv_path")"
    if ! "$python_command" -m venv "$venv_path" || ! venv_has_pip; then
        # A failed venv creation can leave bin/python without pip. Preserve that
        # evidence before retrying so the next installer run is never trapped
        # in the same half-created environment.
        backup_incomplete_venv
        if ! install_ubuntu_venv_support && ! install_debian_venv_support; then
            printf '%s\n' 'Virtual environment creation failed.' >&2
            printf '%s\n' 'On Ubuntu install python3-venv; on Debian 13 install python3.13-venv.' >&2
            exit 1
        fi
        "$python_command" -m venv "$venv_path"
        venv_has_pip || {
            printf 'Virtual environment still has no working pip: %s\n' "$venv_path" >&2
            exit 1
        }
    fi
fi
if [[ "$compact_layout" -eq 0 ]]; then
    venv_tag="$("$venv_python" -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')"
    if [[ "$venv_tag" != "$python_tag" ]]; then
        printf 'Existing virtual environment %s does not match selected CPython %s.\n' "$venv_path" "$python_version" >&2
        exit 1
    fi
fi

pip_arguments=(
    --no-index \
    --only-binary=:all: \
    --no-cache-dir \
    --force-reinstall \
    --find-links "$content_root/wheels" \
    --find-links "$content_root/wheels/dependencies"
)
if [[ "$compact_layout" -eq 0 ]]; then
    pip_arguments+=(--require-hashes)
fi
pip_arguments+=(-r "$payload_root/requirements.lock")
"$venv_python" -m pip install "${pip_arguments[@]}"

"$venv_python" -c "import pymotion as pm; assert pm.lite.__version__ == '1.0.1'; print(pm.lite.__version__)"
if [[ "$compact_layout" -eq 1 ]]; then
    installation_id="$("$python_command" -c 'import json,re,sys; data=json.load(open(sys.argv[1], encoding="utf-8")); value="{}-{}".format(data["target"]["name"], data["release"]["product_bundle"]); print(re.sub(r"[^A-Za-z0-9._-]", "-", value))' "$payload_root/RELEASE-MANIFEST.json")"
else
    installation_id="$("$python_command" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["sha256sums_sha256"][:12])' "$payload_root/RELEASE-MANIFEST.json")"
fi
installation_state_directory="$data_root/pymotion-lite/installations"
installation_state_path="$installation_state_directory/$installation_id.json"
mkdir -p "$installation_state_directory"
"$venv_python" - "$installation_state_path" "$installation_id" "$venv_path" "$python_tag" <<'PY'
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys


state_path = Path(sys.argv[1])
state = {
    "schema": 1,
    "bundle_id": sys.argv[2],
    "venv_path": str(Path(sys.argv[3]).resolve()),
    "python_tag": sys.argv[4],
    "installed_at_utc": datetime.now(timezone.utc).isoformat(),
}
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
PY
printf 'PyMotion Lite SDK installed successfully using the selected Python interpreter.\nPython: %s\n' "$venv_python"
printf 'USB permissions are separate; run sudo %s/install-udev.sh once if required.\n' "$bundle_root"
printf 'Diagnostics: %s/bin/pymotion doctor --offline\n' "$venv_path"
printf 'Open the SDK in VS Code: %s/open-sdk-vscode.sh\n' "$bundle_root"
