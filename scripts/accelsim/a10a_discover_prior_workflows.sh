#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs/a10_prior_reviewpacks

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
search_root="${ACCELSIM_A10_SEARCH_ROOT:-/workspace/repos}"
prior_roots="${ACCELSIM_A10_PRIOR_ROOTS:-}"
max_size="${ACCELSIM_A10_MAX_TEXT_BYTES:-10485760}"
max_files="${ACCELSIM_A10_MAX_FILES:-25000}"
inventory_path=".local_reports/A10A_prior_artifact_inventory_${ts}.csv"
report_path=".local_reports/A10A_prior_artifact_discovery_${ts}.md"
log_path=".local_logs/A10A_prior_artifact_discovery_${ts}.log"

status="PASS"
blocker="none"

exec > >(tee "$log_path") 2>&1

echo "A10A prior artifact discovery"
echo "Start: $start_iso"

python3 - "$inventory_path" "$report_path.tmp" "$search_root" "$prior_roots" "$max_size" "$max_files" "$ts" <<'PY'
import csv
import os
import re
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path

inventory = Path(sys.argv[1])
summary_tmp = Path(sys.argv[2])
search_root = Path(sys.argv[3])
prior_roots = [Path(p) for p in sys.argv[4].split(os.pathsep) if p]
max_size = int(sys.argv[5])
max_files = int(sys.argv[6])
ts = sys.argv[7]
repo_root = Path.cwd().resolve()

exclude_names = {
    ".git", "build", "cmake-build", "hw_run", "traces", "trace",
    ".local_runs", ".local_traces", ".local_logs", "__pycache__",
    "node_modules", "gpu-app-collection",
}
text_ext = {
    ".md", ".txt", ".sh", ".py", ".csv", ".json", ".yaml", ".yml",
    ".log", ".out", ".config", ".cfg", ".ini", ".list",
}
terms = [
    "Mascar", "MASCAR", "mascar", "MeDiC", "MEDIC", "medic",
    "GPGPU-Sim", "gpgpu-sim", "benchmark", "workload", "stats",
    "review_pack", "rodinia", "parboil", "polybench", "sdk", "cutlass",
]
paper_terms = {
    "Mascar": re.compile(r"mascar", re.I),
    "MeDiC": re.compile(r"\bmedic\b|medi c|memory divergence correction", re.I),
}

def clean(s):
    return str(s).replace("\r", "").replace("\n", "")

def paper_hint(text):
    has_mascar = bool(paper_terms["Mascar"].search(text))
    has_medic = bool(paper_terms["MeDiC"].search(text))
    if has_mascar and has_medic:
        return "both"
    if has_mascar:
        return "Mascar"
    if has_medic:
        return "MeDiC"
    return "unknown"

def artifact_type(path):
    low = path.name.lower()
    suf = path.suffix.lower()
    if low.endswith((".tar.gz", ".tgz")):
        return "review_pack"
    if suf == ".csv" and "stat" in low:
        return "stats_csv"
    if suf in {".sh", ".py"}:
        return "script"
    if suf in {".config", ".cfg", ".ini"}:
        return "config"
    if suf in {".log", ".out"}:
        return "log"
    if suf in {".md", ".txt"}:
        return "doc"
    return "unknown_text"

def is_current_bringup_path(path):
    try:
        rel = path.resolve().relative_to(repo_root)
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return False
    if parts[0] in {".local_reports", ".local_logs", ".local_runs", ".local_traces", "review_packs", "hw_run"}:
        return True
    if len(parts) >= 2 and parts[0] == "scripts" and parts[1] == "accelsim":
        return True
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "accelsim_bringup":
        return True
    return False

def likely_text_member(name):
    p = Path(name)
    parts = {part.lower() for part in p.parts}
    if parts & {"trace", "traces", "build", "hw_run", ".git", "gpu-app-collection"}:
        return False
    return p.suffix.lower() in text_ext

roots = []
for root in prior_roots + [search_root]:
    if root.exists() and root not in roots:
        roots.append(root)

rows = []
candidate_repos = set()
candidate_files = 0
review_packs = 0
extracted = 0
scan_errors = []

for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_names and not d.endswith(".egg-info")]
        path = Path(dirpath)
        if any(part in exclude_names for part in path.parts):
            continue
        if (path / ".git").is_dir():
            candidate_repos.add(str(path))
        for name in filenames:
            if candidate_files >= max_files:
                break
            p = path / name
            low = name.lower()
            is_pack = low.endswith((".tar.gz", ".tgz"))
            if not is_pack and p.suffix.lower() not in text_ext:
                continue
            try:
                st = p.stat()
            except OSError as exc:
                scan_errors.append(f"{p}: {exc}")
                continue
            if is_current_bringup_path(p):
                continue
            if st.st_size > max_size and not is_pack:
                continue
            candidate_files += 1
            matched = []
            sample = str(p)
            if is_pack:
                matched = [t for t in terms if t.lower() in low]
            else:
                try:
                    data = p.read_text(errors="replace")[:262144]
                except OSError as exc:
                    scan_errors.append(f"{p}: {exc}")
                    continue
                sample += "\n" + data
                matched = [t for t in terms if re.search(re.escape(t), sample, re.I)]
            if not matched:
                continue
            rel_extract = ""
            notes = ""
            if is_pack:
                review_packs += 1
                listing_path = Path(".local_reports") / f"A10A_tar_listing_{p.name.replace('/', '_')}_{ts}.txt"
                try:
                    listing = subprocess.check_output(["tar", "-tf", str(p)], text=True, errors="replace", timeout=30)
                    listing_path.write_text(listing)
                    notes = f"tar listing: {listing_path}"
                    members = [m for m in listing.splitlines() if likely_text_member(m) and re.search(r"mascar|medic|stats|workload|benchmark|run|summary|readme|csv", m, re.I)]
                    target = Path(".local_runs/a10_prior_reviewpacks") / re.sub(r"[^A-Za-z0-9_.-]", "_", p.name)
                    target.mkdir(parents=True, exist_ok=True)
                    with tarfile.open(p) as tf:
                        for member in members[:80]:
                            info = tf.getmember(member)
                            if info.isfile() and info.size <= max_size:
                                tf.extract(info, path=target)
                                extracted += 1
                    rel_extract = str(target) if members else ""
                except Exception as exc:
                    notes = f"tar inspection failed: {exc}"
            rows.append({
                "artifact_id": f"A10A_{len(rows)+1:05d}",
                "source_root": clean(root),
                "source_path": clean(p),
                "artifact_type": artifact_type(p),
                "paper_hint": paper_hint(sample),
                "matched_terms": ";".join(sorted(set(matched), key=str.lower)),
                "size_bytes": st.st_size,
                "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(),
                "extracted_path": clean(rel_extract),
                "notes": notes,
            })
        if candidate_files >= max_files:
            break

with inventory.open("w", newline="") as f:
    fields = ["artifact_id","source_root","source_path","artifact_type","paper_hint","matched_terms","size_bytes","mtime","extracted_path","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

top_mascar = [r["source_path"] for r in rows if r["paper_hint"] in {"Mascar", "both"}][:12]
top_medic = [r["source_path"] for r in rows if r["paper_hint"] in {"MeDiC", "both"}][:12]
summary_tmp.write_text("\n".join([
    f"roots={';'.join(map(str, roots))}",
    f"candidate_repos={len(candidate_repos)}",
    f"candidate_files={candidate_files}",
    f"artifact_rows={len(rows)}",
    f"review_packs={review_packs}",
    f"paper_rows={sum(1 for r in rows if r['paper_hint'] in {'Mascar','MeDiC','both'})}",
    f"extracted_members={extracted}",
    f"scan_errors={len(scan_errors)}",
    "top_mascar=" + "|".join(top_mascar),
    "top_medic=" + "|".join(top_medic),
]))
PY

artifact_line_count="$(wc -l < "$inventory_path" 2>/dev/null || printf '1')"
artifact_rows=$((artifact_line_count - 1))
[ "$artifact_rows" -lt 0 ] && artifact_rows=0
review_packs="$(awk -F, 'NR>1 && $4=="review_pack"{c++} END{print c+0}' "$inventory_path" 2>/dev/null || echo 0)"
paper_rows="$(sed -n 's/^paper_rows=//p' "$report_path.tmp" 2>/dev/null | head -1)"
candidate_repos="$(sed -n 's/^candidate_repos=//p' "$report_path.tmp" 2>/dev/null | head -1)"
candidate_files="$(sed -n 's/^candidate_files=//p' "$report_path.tmp" 2>/dev/null | head -1)"
extracted_members="$(sed -n 's/^extracted_members=//p' "$report_path.tmp" 2>/dev/null | head -1)"

if [ "$artifact_rows" -eq 0 ] || [ "${paper_rows:-0}" -eq 0 ]; then
  status="BLOCKED_NO_PRIOR_ARTIFACTS"
  blocker="bounded search found no Mascar/MeDiC prior artifact evidence"
elif [ "$review_packs" -eq 0 ]; then
  status="PARTIAL_PASS_NO_REVIEW_PACKS"
fi

if [ -f 0 ] && [ "$(wc -c < 0)" -le 16 ]; then
  if [ -z "$(git status --short -- 0)" ] || git status --short -- 0 | grep -q '^?? 0$'; then
    rm -f 0
  fi
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A10A Prior Artifact Discovery

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a10a_discover_prior_workflows.sh\`
- Log: \`$log_path\`
- Inventory CSV: \`$inventory_path\`
- Search root: \`$search_root\`
- Explicit prior roots: \`${prior_roots:-}\`
- Blocker: $blocker

## Bounded Search

- Excluded dirs: .git, build, cmake-build, hw_run, traces, trace, .local_runs, .local_traces, .local_logs, __pycache__, node_modules
- Text size limit: $max_size bytes
- Max candidate files: $max_files
- Candidate repos: ${candidate_repos:-0}
- Candidate files inspected: ${candidate_files:-0}
- Artifact rows: $artifact_rows
- Mascar/MeDiC paper-hint rows: ${paper_rows:-0}
- Review packs: $review_packs
- Extracted review-pack members: ${extracted_members:-0}

## Top Mascar Artifacts

\`\`\`
$(sed -n 's/^top_mascar=//p' "$report_path.tmp" | tr '|' '\n' | sed -n '1,12p')
\`\`\`

## Top MeDiC Artifacts

\`\`\`
$(sed -n 's/^top_medic=//p' "$report_path.tmp" | tr '|' '\n' | sed -n '1,12p')
\`\`\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF
rm -f "$report_path.tmp"

echo "A10A report: $report_path"
echo "A10A inventory: $inventory_path"
echo "A10A status: $status"

case "$status" in
  PASS|PARTIAL_PASS_NO_REVIEW_PACKS|BLOCKED_NO_PRIOR_ARTIFACTS) exit 0 ;;
  *) exit 1 ;;
esac
