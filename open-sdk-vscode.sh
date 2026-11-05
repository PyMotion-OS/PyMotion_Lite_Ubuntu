#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
data_root="${XDG_DATA_HOME:-${HOME}/.local/share}"
no_launch=0
if [[ "${1:-}" == "--no-launch" ]]; then
    no_launch=1
    shift
fi
[[ "$#" -eq 0 ]] || { printf 'Usage: %s [--no-launch]\n' "$0" >&2; exit 2; }

payload_root="$bundle_root"
[[ -f "$bundle_root/RELEASE-MANIFEST.json" ]] || payload_root="$bundle_root/internal"
manifest_path="$payload_root/RELEASE-MANIFEST.json"
[[ -f "$manifest_path" ]] || { printf 'Signed release manifest is missing. Run this launcher from a complete customer bundle.\n' >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { printf 'python3 is required to open the SDK workspace.\n' >&2; exit 1; }

compact_layout="$(python3 -c 'import json,sys; print("1" if json.load(open(sys.argv[1], encoding="utf-8")).get("install_policy", {}).get("compact_layout") is True else "0")' "$manifest_path")"
if [[ "$compact_layout" == "1" ]]; then
    installation_id="$(python3 -c 'import json,re,sys; data=json.load(open(sys.argv[1], encoding="utf-8")); value="{}-{}".format(data["target"]["name"], data["release"]["product_bundle"]); print(re.sub(r"[^A-Za-z0-9._-]", "-", value))' "$manifest_path")"
else
    installation_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["sha256sums_sha256"][:12])' "$manifest_path")"
fi
installation_state="$data_root/pymotion-lite/installations/$installation_id.json"
[[ -f "$installation_state" ]] || { printf 'Installed SDK environment was not found. Run %s/setup-ubuntu.sh first.\n' "$bundle_root" >&2; exit 1; }
venv_path="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["venv_path"])' "$installation_state")"
sdk_python="$venv_path/bin/python"
[[ -x "$sdk_python" ]] || { printf 'Installed SDK Python was not found: %s\n' "$sdk_python" >&2; exit 1; }
"$sdk_python" -c "import pymotion as pm; assert pm.lite.__version__ == '1.0.1'" \
    || { printf 'Installed SDK import check failed. Run %s/setup-ubuntu.sh again.\n' "$bundle_root" >&2; exit 1; }

python_runner="$bundle_root/run-sdk-python.sh"
[[ -x "$python_runner" ]] || { printf 'Signed SDK Python runner is missing or not executable.\n' >&2; exit 1; }
workspace_directory="$data_root/pymotion-lite/workspaces/pymotion-lite-$installation_id"
project_directory="$workspace_directory/project"
editable_examples="$project_directory/examples"
mkdir -p "$project_directory"
examples_root="$payload_root/examples"
[[ "$compact_layout" == "0" ]] || examples_root="$bundle_root/examples"
[[ -d "$editable_examples" ]] || cp -a "$examples_root" "$editable_examples"
if [[ "$compact_layout" == "0" ]]; then
    [[ -f "$project_directory/README.md" ]] || cp "$payload_root/docs/README.md" "$project_directory/README.md"
    [[ -f "$project_directory/SDK_USER_MANUAL.md" ]] || cp "$payload_root/docs/SDK_USER_MANUAL.md" "$project_directory/SDK_USER_MANUAL.md"
fi

workspace_path="$workspace_directory/pymotion-lite.code-workspace"
python3 - "$workspace_path" "$project_directory" "$sdk_python" "$python_runner" <<'PY'
from __future__ import annotations

import json
from pathlib import Path
import shlex
import sys


workspace_path = Path(sys.argv[1])
project_directory, sdk_python, python_runner = sys.argv[2:]
executor = f"bash {shlex.quote(python_runner)} {shlex.quote(sdk_python)}"
workspace = {
    "folders": [{"name": "PyMotion Lite SDK", "path": project_directory}],
    "settings": {
        "python.defaultInterpreterPath": sdk_python,
        "python.terminal.activateEnvironment": True,
        "code-runner.executorMap": {"python": executor},
        "code-runner.runInTerminal": True,
        "code-runner.ignoreSelection": True,
    },
}
workspace_path.write_text(json.dumps(workspace, indent=2) + "\n", encoding="utf-8")
PY

printf 'PyMotion Lite VS Code workspace is ready.\n'
printf 'Python: %s\n' "$sdk_python"
printf 'Editable examples: %s\n' "$editable_examples"
printf 'Workspace: %s\n' "$workspace_path"
[[ "$no_launch" -eq 0 ]] || exit 0
command -v code >/dev/null 2>&1 || { printf 'Visual Studio Code was not found. Install it, then run open-sdk-vscode.sh again.\n' >&2; exit 1; }
code --new-window "$workspace_path"
