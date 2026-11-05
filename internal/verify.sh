#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
cd "$bundle_root"

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

[[ ! -f NOT_FOR_DISTRIBUTION.txt ]] || fail "this staging bundle is not authorized for installation"
evaluation=0
[[ ! -f EVALUATION_ONLY.txt ]] || evaluation=1
for required_file in RELEASE-MANIFEST.json RELEASE-MANIFEST.sig RELEASE-CERTIFICATE.cer requirements.lock; do
    [[ -f "$required_file" ]] || fail "missing release integrity file: $required_file"
done

command -v python3 >/dev/null 2>&1 || fail "python3 is required for release verification"
command -v openssl >/dev/null 2>&1 || fail "openssl is required for release verification"
command -v base64 >/dev/null 2>&1 || fail "base64 is required for release verification"

verification_dir="$(mktemp -d "${TMPDIR:-/tmp}/pymotion-verify.XXXXXX")"
cleanup() {
    case "$verification_dir" in
        "${TMPDIR:-/tmp}"/pymotion-verify.*) rm -rf -- "$verification_dir" ;;
        *) printf 'Refusing to clean unexpected verification directory: %s\n' "$verification_dir" >&2 ;;
    esac
}
trap cleanup EXIT

openssl x509 -inform DER -in RELEASE-CERTIFICATE.cer -out "$verification_dir/release-cert.pem" \
    >/dev/null 2>&1 || fail "release certificate is not valid DER X.509"
if [[ "$evaluation" -eq 0 ]]; then
    # The leaf certificate inside a production bundle is never a trust anchor.
    # Operations installs the release CA independently, or supplies an equally
    # independent path through this environment variable.
    trusted_ca="${PYMOTION_TRUSTED_CA_FILE:-/etc/pymotion/trust/release-ca.pem}"
    [[ -f "$trusted_ca" ]] || fail "trusted release CA is missing: $trusted_ca"
    openssl verify -CAfile "$trusted_ca" "$verification_dir/release-cert.pem" \
        >/dev/null 2>&1 || fail "release certificate is not trusted by the configured CA"
fi
openssl x509 -in "$verification_dir/release-cert.pem" -pubkey -noout \
    > "$verification_dir/release-public-key.pem"
base64 --decode RELEASE-MANIFEST.sig > "$verification_dir/release-manifest.sig" \
    2>/dev/null || fail "release signature is not valid base64"
openssl dgst -sha256 \
    -verify "$verification_dir/release-public-key.pem" \
    -signature "$verification_dir/release-manifest.sig" \
    RELEASE-MANIFEST.json >/dev/null 2>&1 \
    || fail "release manifest signature verification failed"

python3 - "$bundle_root" <<'PY'
from __future__ import annotations

import hashlib
import json
import platform
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
import sys
import zipfile


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


root = Path(sys.argv[1]).resolve()
manifest_path = root / "RELEASE-MANIFEST.json"
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    fail(f"invalid release manifest: {type(exc).__name__}")

if manifest.get("schema") != 1:
    fail("release manifest is not a schema-1 bundle")
evaluation_marker = (root / "EVALUATION_ONLY.txt").is_file()
if evaluation_marker:
    if manifest.get("evaluation") is not True or manifest.get("production") is not False:
        fail("evaluation marker and signed manifest disagree")
else:
    if manifest.get("production") is not True or manifest.get("evaluation") is True:
        fail("release manifest is not a production bundle")
release = manifest.get("release")
if not isinstance(release, dict):
    fail("release metadata is missing")
install_policy = manifest.get("install_policy", {})
compact_layout = (
    isinstance(install_policy, dict)
    and install_policy.get("compact_layout") is True
    and install_policy.get("verify_file_hashes") is False
    and install_policy.get("compare_python_version") is False
)
if not evaluation_marker and (
    release.get("release_state") != "released" or release.get("hil_status") != "PASS"
):
    fail("release gates are incomplete")

target = manifest.get("target")
if not isinstance(target, dict) or target.get("os") not in {"ubuntu", "debian"}:
    fail("bundle is not a supported Linux target")
if platform.system() != "Linux":
    fail("Linux bundle can only be installed on Linux")
machine = platform.machine().lower()
architecture = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine)
if architecture is None or architecture != target.get("architecture"):
    fail(f"bundle architecture {target.get('architecture')!r} does not match host {machine!r}")
os_release: dict[str, str] = {}
try:
    for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        os_release[key] = value.strip().strip('"').strip("'")
except (OSError, UnicodeError) as exc:
    fail(f"cannot read /etc/os-release: {type(exc).__name__}")
target_os = target["os"]
if target_os == "ubuntu":
    ubuntu_versions = target.get("ubuntu_versions")
    if not isinstance(ubuntu_versions, list) or not ubuntu_versions:
        fail("signed Ubuntu version policy is missing")
    if os_release.get("ID", "").lower() != "ubuntu":
        fail("Ubuntu bundles require Ubuntu")
    host_ubuntu = os_release.get("VERSION_ID", "")
    if host_ubuntu not in ubuntu_versions:
        fail(f"Ubuntu {host_ubuntu or 'unknown'} is unsupported; expected {', '.join(ubuntu_versions)}")
else:
    debian_versions = target.get("debian_versions")
    if (
        target.get("name") != "debian13-arm64"
        or target.get("architecture") != "arm64"
        or debian_versions != ["13"]
        or target.get("python_tags") != ["cp313"]
    ):
        fail("signed Debian 13 ARM64/cp313 policy is invalid")
    if os_release.get("ID", "").lower() != "debian":
        fail("Debian bundles require Debian")
    if os_release.get("VERSION_ID", "") not in debian_versions:
        fail("Debian 13 is required")
if compact_layout:
    required_payload = [
        root / "install.sh",
        root / "requirements.lock",
        root.parent / "wheels",
        root.parent / "examples",
        root.parent / "udev",
    ]
    missing = [path.name for path in required_payload if not path.exists()]
    if missing:
        fail("bundle payload is incomplete: " + ", ".join(missing))
    if evaluation_marker:
        print("WARNING: INTERNAL EVALUATION BUILD: production release and HIL gates are incomplete.")
    print("PyMotion Lite release signature and target are valid; file hash checks are disabled by package policy.")
    raise SystemExit(0)

if platform.python_implementation() != "CPython" or not ((3, 10) <= sys.version_info < (3, 15)):
    fail("PyMotion Lite requires CPython 3.10 through 3.14")

entries = manifest.get("files")
if not isinstance(entries, list) or not entries:
    fail("release manifest contains no payload files")
seen: set[str] = set()
for entry in entries:
    if not isinstance(entry, dict):
        fail("release manifest contains an invalid file entry")
    relative = entry.get("path")
    if not isinstance(relative, str) or relative in seen:
        fail("release manifest contains an invalid or duplicate path")
    seen.add(relative)
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or "\\" in relative:
        fail(f"unsafe release manifest path: {relative!r}")
    local = root.joinpath(*pure.parts)
    try:
        local.resolve().relative_to(root)
    except ValueError:
        fail(f"release manifest path escapes bundle: {relative!r}")
    if local.is_symlink() or not local.is_file():
        fail(f"missing or symbolic signed release file: {relative}")
    if local.stat().st_size != entry.get("bytes"):
        fail(f"release file size mismatch: {relative}")
    digest = hashlib.sha256(local.read_bytes()).hexdigest().upper()
    if digest != str(entry.get("sha256", "")).upper():
        fail(f"release file hash mismatch: {relative}")

sums_digest = hashlib.sha256((root / "SHA256SUMS.txt").read_bytes()).hexdigest().upper()
if sums_digest != str(manifest.get("sha256sums_sha256", "")).upper():
    fail("SHA256SUMS.txt does not match the signed release manifest")

integrity_names = {
    "RELEASE-MANIFEST.json",
    "RELEASE-MANIFEST.sig",
    "RELEASE-CERTIFICATE.cer",
    "SHA256SUMS.txt",
}
actual = {
    path.relative_to(root).as_posix()
    for path in root.rglob("*")
    if path.is_file()
}
unexpected = actual - seen - integrity_names
if unexpected:
    fail("bundle contains unsigned extra files: " + ", ".join(sorted(unexpected)))

main_wheels = sorted(root.glob("wheels/pymotion_lite-*.whl"))
if not main_wheels:
    fail("bundle contains no PyMotion Lite wheel")
python_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
platform_tag = (
    "manylinux_2_28_x86_64" if architecture == "amd64" else "manylinux_2_28_aarch64"
)
wheel_python_tags: dict[Path, str] = {}
for wheel in main_wheels:
    try:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            wheel_metadata = [name for name in names if name.endswith(".dist-info/WHEEL")]
            if len(wheel_metadata) != 1:
                fail(f"SDK wheel needs exactly one WHEEL metadata file: {wheel.name}")
            metadata = BytesParser().parsebytes(archive.read(wheel_metadata[0]))
            tags = metadata.get_all("Tag", [])
    except (OSError, zipfile.BadZipFile) as exc:
        fail(f"cannot inspect SDK wheel {wheel.name}: {type(exc).__name__}")
    metadata_platforms: set[str] = set()
    compatible_python_tags: set[str] = set()
    for tag in tags:
        parts = tag.split("-", 2)
        if len(parts) != 3:
            continue
        platforms = set(parts[2].split("."))
        metadata_platforms.update(platforms)
        if parts[0] == parts[1] and platform_tag in platforms:
            compatible_python_tags.add(parts[0])
    forbidden_platforms = sorted(
        item
        for item in metadata_platforms
        if item.startswith("linux_") or item.startswith("musllinux_")
    )
    if forbidden_platforms:
        fail(f"SDK wheel contains forbidden platform tags: {wheel.name}")
    if len(compatible_python_tags) != 1:
        fail(f"SDK wheel does not have one CPython/{platform_tag} tag: {wheel.name}")
    wheel_python_tag = next(iter(compatible_python_tags))
    filename_parts = wheel.name.removesuffix(".whl").rsplit("-", 3)
    if (
        len(filename_parts) != 4
        or filename_parts[1] != wheel_python_tag
        or filename_parts[2] != wheel_python_tag
        or platform_tag not in filename_parts[3].split(".")
    ):
        fail(f"SDK wheel filename does not match its signed compatibility tag: {wheel.name}")
    wheel_python_tags[wheel] = wheel_python_tag

matching = [wheel for wheel, tag in wheel_python_tags.items() if tag == python_tag]
if len(matching) != 1:
    fail(f"expected exactly one {python_tag}/{platform_tag} SDK wheel, found {len(matching)}")

if evaluation_marker:
    print("WARNING: INTERNAL EVALUATION BUILD: production release and HIL gates are incomplete.")
print("PyMotion Lite release signature, target and all file hashes are valid.")
PY
