#!/usr/bin/env bash
# Copy a completed M4A archive to the main server and prove source/destination equality.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: copyback_m4a_bundle.sh --ssh-target HOST --remote-archive ABS_PATH --destination DIR

Run this on the main development server only after the remote archive passed
its own tar/SHA256 integrity checks. It copies the archive and its .sha256
sidecar with rsync --partial, independently compares archive SHA256 values,
and writes a small COPYBACK_VERIFICATION.md beside the copied artifact.
EOF
}

ssh_target=""; remote_archive=""; destination=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ssh-target) ssh_target="$2"; shift 2 ;;
    --remote-archive) remote_archive="$2"; shift 2 ;;
    --destination) destination="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$ssh_target" && -n "$remote_archive" && -n "$destination" ]] || { usage >&2; exit 2; }
[[ "$remote_archive" == /* ]] || { echo "error: --remote-archive must be absolute" >&2; exit 2; }
mkdir -p "$destination"
remote_quoted="$(printf '%q' "$remote_archive")"
remote_sha="$(ssh -o BatchMode=yes "$ssh_target" "sha256sum -- $remote_quoted" | awk '{print $1}')"
[[ "$remote_sha" =~ ^[0-9a-f]{64}$ ]] || { echo "error: could not obtain remote archive SHA256" >&2; exit 1; }
rsync -aP --partial --protect-args "$ssh_target:$remote_archive" "$ssh_target:$remote_archive.sha256" "$destination/"
archive_name="$(basename "$remote_archive")"; local_archive="$destination/$archive_name"
[[ -s "$local_archive" && -s "$local_archive.sha256" ]] || { echo "error: copied archive or sidecar is missing" >&2; exit 1; }
local_sha="$(sha256sum "$local_archive" | awk '{print $1}')"
[[ "$remote_sha" == "$local_sha" ]] || { echo "error: archive SHA256 mismatch remote=$remote_sha local=$local_sha" >&2; exit 1; }
record="$destination/COPYBACK_VERIFICATION.md"
printf '# M4A archive copy-back verification\n\n- UTC: %s\n- SSH target: `%s`\n- Remote archive: `%s`\n- Local archive: `%s`\n- Remote SHA256: `%s`\n- Local SHA256: `%s`\n- Result: `PASS`\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$ssh_target" "$remote_archive" "$local_archive" "$remote_sha" "$local_sha" > "$record"
printf 'PASS copied=%s sha256=%s record=%s\n' "$local_archive" "$local_sha" "$record"
