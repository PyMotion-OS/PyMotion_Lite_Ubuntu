#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
if [[ -n "${PYMOTION_PYTHON:-}" ]]; then
    python_command="$PYMOTION_PYTHON"
elif [[ -x /usr/bin/python3 ]]; then
    python_command=/usr/bin/python3
else
    python_command=python3
fi
data_root="${XDG_DATA_HOME:-${HOME}/.local/share}"

[[ "${EUID}" -ne 0 ]] || {
    printf '%s\n' 'Run this setup as your normal desktop user, not with sudo.' >&2
    exit 1
}
[[ -r /etc/os-release ]] || {
    printf '%s\n' 'Ubuntu 24.04 LTS amd64 is required.' >&2
    exit 1
}
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" && "${VERSION_ID:-}" == "24.04" ]] || {
    printf 'Ubuntu 24.04 LTS amd64 is required; found %s %s.\n' \
        "${ID:-unknown}" "${VERSION_ID:-unknown}" >&2
    exit 1
}
case "$(uname -m)" in
    x86_64|amd64) ;;
    *) printf 'Ubuntu requires amd64; found %s.\n' "$(uname -m)" >&2; exit 1 ;;
esac
command -v sudo >/dev/null 2>&1 || {
    printf '%s\n' 'sudo is required to install USB permissions.' >&2
    exit 1
}

printf '%s\n' 'PyMotion Lite Ubuntu setup'
printf '%s\n' 'Administrator access is used only for Ubuntu packages and USB permissions.'
sudo -v

compact_layout=0
if [[ -f "$bundle_root/internal/install.sh" ]]; then
    compact_layout=1
    PYMOTION_PYTHON="$python_command" bash "$bundle_root/internal/install.sh"
else
    PYMOTION_PYTHON="$python_command" bash "$bundle_root/install.sh"
fi
bash "$bundle_root/install-udev.sh"

login_user="$(id -un)"
group_changed=0
if ! id -nG "$login_user" | tr ' ' '\n' | grep -Fxq dialout; then
    printf 'Adding user %s to the dialout group.\n' "$login_user"
    sudo usermod -aG dialout "$login_user"
    group_changed=1
fi

if [[ "$compact_layout" -eq 1 ]]; then
    venv_path="${PYMOTION_VENV:-${data_root}/pymotion-lite/venv-ubuntu}"
else
    python_tag="$("$python_command" -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')"
    venv_path="${PYMOTION_VENV:-${data_root}/pymotion-lite/venv-${python_tag}}"
fi
sdk_command="$venv_path/bin/pymotion"
[[ -x "$sdk_command" ]] || {
    printf 'Installed PyMotion command was not found: %s\n' "$sdk_command" >&2
    exit 1
}

# Prepare the editable example workspace without requiring VS Code to exist.
bash "$bundle_root/open-sdk-vscode.sh" --no-launch

printf '\n%s\n' 'Current diagnostics:'
set +e
"$sdk_command" doctor
doctor_status="$?"
set -e

printf '\n%s\n' 'Setup finished.'
printf '%s\n' '1. Disconnect and reconnect the PyMotion Lite USB cable.'
if [[ "$group_changed" -eq 1 ]]; then
    printf '%s\n' '2. Log out of Ubuntu completely and log in again to activate dialout access.'
else
    printf '%s\n' '2. Your current user is already in the dialout group.'
fi
printf '3. Set the device token: export PYMOTION_AUTH_TOKEN=%q\n' 'your-device-token'
printf '4. Run diagnostics: %q doctor\n' "$sdk_command"
printf '5. Open examples: bash %q/open-sdk-vscode.sh\n' "$bundle_root"
if [[ "$doctor_status" -ne 0 ]]; then
    printf '%s\n' 'The current diagnostic failure may clear after USB reconnect and login refresh.'
fi
