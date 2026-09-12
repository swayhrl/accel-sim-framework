#!/usr/bin/env bash
# Idempotent, offline-only AutoDL environment bootstrap for C16 Lane G.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=""
WHEELHOUSE="${C16_WHEELHOUSE:-}"
VENV_DIR="${C16_VENV:-/root/autodl-tmp/c16/env}"
PYTHON_BIN="${C16_PYTHON:-python3}"

usage() {
  printf '%s\n' "usage: $0 (--dry-run|--install) --wheelhouse PATH [--venv PATH] [--python PYTHON3.10]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|--install) [[ -z "$MODE" ]] || { usage >&2; exit 2; }; MODE="$1"; shift ;;
    --wheelhouse) WHEELHOUSE="$2"; shift 2 ;;
    --venv) VENV_DIR="$2"; shift 2 ;;
    --python) PYTHON_BIN="$2"; shift 2 ;;
    --help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

[[ -n "$MODE" && -n "$WHEELHOUSE" ]] || { usage >&2; exit 2; }
LOCK="$SCRIPT_DIR/requirements.lock"
MANIFEST="$WHEELHOUSE/WHEELHOUSE_MANIFEST.tsv"

if [[ "$MODE" == "--dry-run" ]]; then
  printf '%s\n' "C16 bootstrap dry-run only: no GPU query, no download, no pip install"
  printf 'python=%s\n' "$($PYTHON_BIN --version)"
  printf 'wheelhouse=%s\nmanifest=%s\nvenv=%s\nlock_sha256=%s\n' "$WHEELHOUSE" "$MANIFEST" "$VENV_DIR" "$(sha256sum "$LOCK" | awk '{print $1}')"
  printf '%s\n' "planned: verify imported hashes; create/reuse venv; install only local hash-closed wheels; pip check"
  exit 0
fi

[[ -d "$WHEELHOUSE" && -f "$MANIFEST" ]] || { printf '%s\n' "missing hash-closed wheelhouse" >&2; exit 2; }
"$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 10) else 2)' || { printf '%s\n' "C16 bootstrap requires CPython 3.10" >&2; exit 2; }
"$PYTHON_BIN" "$SCRIPT_DIR/wheelhouse_verify.py" --wheelhouse "$WHEELHOUSE" --manifest "$MANIFEST" --requirements "$LOCK"
"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --no-index --find-links "$WHEELHOUSE" --only-binary=:all: -r "$LOCK"
"$VENV_DIR/bin/python" -m pip check
printf '%s\n' "PASS C16 offline wheelhouse bootstrap: $VENV_DIR"
