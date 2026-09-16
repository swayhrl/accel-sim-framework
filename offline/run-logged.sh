#!/usr/bin/env bash
set -u
repo="$(cd "$(dirname "$0")/.." && pwd)"
bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
name="$1"; shift
mkdir -p "$bundle/logs"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"; log="$bundle/logs/${name}-${stamp}.log"; rc="$bundle/logs/${name}-${stamp}.rc"
set +e
timeout "${OFFLINE_TIMEOUT_SECONDS:-600}" "$@" >"$log" 2>&1
status=$?
set -e
printf '%s\n' "$status" >"$rc"
cp "$log" "$bundle/logs/${name}-latest.log"
cp "$rc" "$bundle/logs/${name}-latest.rc"
printf 'LOG=%s\nRC=%s\nSTATUS=%s\n' "$log" "$rc" "$status"
exit "$status"
