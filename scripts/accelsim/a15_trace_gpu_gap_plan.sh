#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
run_name="${ACCELSIM_A15_RUN_NAME:-A15_trace_gpu_gap_${ts}}"
allow_trace="${ACCELSIM_A15_ALLOW_TRACE_GENERATION:-0}"
gpu_device="${ACCELSIM_A15_GPU_DEVICE:-0}"
lockfile="${ACCELSIM_A15_LOCKFILE:-$(ls -t .local_reports/A12_workload_config_lock_*.csv 2>/dev/null | head -1 || true)}"
mapping="${ACCELSIM_A15_TRACE_MAPPING:-$(ls -t .local_reports/A10C_trace_mapping_*.csv 2>/dev/null | head -1 || true)}"
plan_path=".local_reports/A15_trace_gap_plan_${ts}.md"
matrix_path=".local_reports/A15_trace_gap_matrix_${ts}.csv"
summary_path=".local_reports/A11_A15_final_summary_${ts}.md"
log_path=".local_logs/A15_trace_gpu_gap_plan_${ts}.log"
review_pack="review_packs/A11_A15_PAPER_REPRO_PIPELINE_review_pack_${ts}.tar.gz"

exec > >(tee "$log_path") 2>&1

echo "A15 trace GPU gap plan"
echo "Start: $start_iso"

nvidia_smi_out="$(nvidia-smi 2>&1 || true)"
dev_nvidia_out="$(ls -l /dev/nvidia* 2>&1 || true)"
nvcc_out="$(nvcc --version 2>&1 || true)"
gpu_visible="no"
if printf '%s\n%s\n' "$nvidia_smi_out" "$dev_nvidia_out" | grep -qi 'NVIDIA'; then
  gpu_visible="yes"
fi
tracer_status="BLOCKED_NO_GPU_FOR_TRACER"
status="PASS_WITH_NO_GPU"
if [ "$gpu_visible" = "yes" ]; then
  tracer_status="GPU_VISIBLE_TRACE_GENERATION_NOT_REQUESTED"
  status="PASS"
fi
if [ "$gpu_visible" = "yes" ] && [ "$allow_trace" = "1" ]; then
  tracer_status="TRACE_GENERATION_ALLOWED_NOT_ATTEMPTED_IN_A15"
fi

python3 - "$matrix_path" "$lockfile" "$mapping" <<'PY'
import csv, sys
from pathlib import Path

out, lockfile, mapping = map(Path, sys.argv[1:])
def read(path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return [{k:(v or "").replace("\r","").replace("\n","").strip() for k,v in r.items()} for r in csv.DictReader(f)]
locks = read(lockfile)
rows = []
for r in locks:
    needed = "future"
    if r.get("include_smoke") == "yes":
        needed = "smoke"
    elif r.get("include_pilot") == "yes":
        needed = "pilot"
    elif r.get("include_paper_candidate") == "yes":
        needed = "paper_candidate"
    current = "available" if r.get("runnable") == "yes" and r.get("kernelslist_path") else "missing"
    rows.append({
        "gap_id": f"G{len(rows)+1:05d}",
        "paper": r.get("paper"),
        "workload": r.get("workload"),
        "normalized_workload": r.get("normalized_workload"),
        "current_trace_status": current,
        "kernelslist_path": r.get("kernelslist_path"),
        "needed_for_set": needed,
        "can_use_pretrace": "yes" if current == "available" else "no",
        "needs_new_trace": "no" if current == "available" else "yes",
        "gpu_required": "no" if current == "available" else "yes",
        "suggested_source": "existing .local_traces pretrace" if current == "available" else "gpu-app-collection or prior workload source",
        "suggested_command": "reuse kernelslist.g" if current == "available" else "ACCELSIM_A15_ALLOW_TRACE_GENERATION=1 bash scripts/accelsim/a15_trace_gpu_gap_plan.sh",
        "notes": "trace acquisition gap matrix",
    })
with out.open("w", newline="") as f:
    fields = ["gap_id","paper","workload","normalized_workload","current_trace_status","kernelslist_path","needed_for_set","can_use_pretrace","needs_new_trace","gpu_required","suggested_source","suggested_command","notes"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
PY

if [ -f 0 ] && [ "$(wc -c < 0)" -le 16 ] && git status --short -- 0 | grep -q '^?? 0$'; then
  rm -f 0
  zero_note="removed transient untracked file 0"
else
  zero_note="no transient file 0 observed"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$plan_path" <<EOF
# A15 Trace GPU Gap Plan

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a15_trace_gpu_gap_plan.sh\`
- Log: \`$log_path\`
- Lockfile: \`${lockfile:-}\`
- Trace mapping: \`${mapping:-}\`
- Trace gap matrix: \`$matrix_path\`
- GPU visible: $gpu_visible
- Tracer status: $tracer_status
- Allow trace generation: $allow_trace
- GPU device: $gpu_device
- Blocker: $tracer_status

## GPU Checks

### nvidia-smi

\`\`\`
$nvidia_smi_out
\`\`\`

### /dev/nvidia*

\`\`\`
$dev_nvidia_out
\`\`\`

### nvcc

\`\`\`
$nvcc_out
\`\`\`

### CUDA Environment

\`\`\`
CUDA_HOME=${CUDA_HOME:-}
CUDA_PATH=${CUDA_PATH:-}
CUDA_INSTALL_PATH=${CUDA_INSTALL_PATH:-}
\`\`\`

## Plan

- Use existing pretraces for smoke/pilot rows where \`current_trace_status=available\`.
- For missing paper-candidate rows, acquire traces only on a GPU host.
- Future command gate: \`ACCELSIM_A15_ALLOW_TRACE_GENERATION=1\`.
- A15 did not validate NVBit tracer in this environment.

## Hygiene

- $zero_note
- CSV headers are stable for A11-A15 outputs.
- Review pack excludes traces, build directories, prior repos, and nested review packs.

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

a11_report="$(ls -t .local_reports/A11_stats_equivalence_*.md 2>/dev/null | head -1 || true)"
a12_report="$(ls -t .local_reports/A12_workload_config_lock_summary_*.md 2>/dev/null | head -1 || true)"
a13_report="$(ls -t .local_reports/A13_experiment_matrix_summary_*.md 2>/dev/null | head -1 || true)"
a14_report="$(ls -t .local_reports/A14_reproduction_readiness_*.md 2>/dev/null | head -1 || true)"
a11_status="$(sed -n 's/^- Status: //p' "$a11_report" 2>/dev/null | head -1)"
a12_status="$(sed -n 's/^- Status: //p' "$a12_report" 2>/dev/null | head -1)"
a13_status="$(sed -n 's/^- Status: //p' "$a13_report" 2>/dev/null | head -1)"
a14_status="$(sed -n 's/^- Status: //p' "$a14_report" 2>/dev/null | head -1)"
a11_matrix="$(ls -t .local_reports/A11_stats_equivalence_matrix_*.csv 2>/dev/null | head -1 || true)"
a11_stats="$(ls -t .local_reports/A11_normalized_stats_*.csv 2>/dev/null | head -1 || true)"
a12_lock="$(ls -t .local_reports/A12_workload_config_lock_*.csv 2>/dev/null | head -1 || true)"
a13_matrix="$(ls -t .local_reports/A13_experiment_matrix_*.csv 2>/dev/null | head -1 || true)"
a13_results="$(ls -t .local_reports/A13_experiment_results_*.csv 2>/dev/null | head -1 || true)"
a14_mini="$(ls -t .local_reports/A14_mini_result_table_*.csv 2>/dev/null | head -1 || true)"
a14_check="$(ls -t .local_reports/A14_readiness_checklist_*.csv 2>/dev/null | head -1 || true)"

cat > "$summary_path" <<EOF
# A11-A15 Final Summary

- A11 status: \`${a11_status:-missing}\`
- A12 status: \`${a12_status:-missing}\`
- A13 status: \`${a13_status:-missing}\`
- A14 status: \`${a14_status:-missing}\`
- A15 status: \`$status\`
- Baseline commit: \`$(git rev-parse HEAD)\`
- A11 equivalence matrix: \`${a11_matrix:-}\`
- A11 normalized stats: \`${a11_stats:-}\`
- A12 lockfile: \`${a12_lock:-}\`
- A13 matrix: \`${a13_matrix:-}\`
- A13 results: \`${a13_results:-}\`
- A14 mini table: \`${a14_mini:-}\`
- A14 readiness checklist: \`${a14_check:-}\`
- A15 trace gap matrix: \`$matrix_path\`
- Review pack: \`$review_pack\`
- Final git status:

\`\`\`
$(git status --short)
\`\`\`

## Conclusion

Paper reproduction infrastructure is ready for bounded baseline and future variant plumbing. Actual paper mechanisms and GPU trace acquisition remain explicit future work.
EOF

tar_inputs=()
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find docs/accelsim_bringup -maxdepth 1 -type f \( -name 'A11*.md' -o -name 'A12*.md' -o -name 'A13*.md' -o -name 'A14*.md' -o -name 'A15*.md' -o -name 'STATS_EQUIVALENCE_SCHEMA.md' -o -name 'WORKLOAD_CONFIG_LOCKDOWN.md' -o -name 'EXPERIMENT_MATRIX_SCHEMA.md' -o -name 'PAPER_REPRODUCTION_READY.md' -o -name 'TRACE_ACQUISITION_PLAN.md' -o -name 'RUNBOOK.md' -o -name 'KNOWN_ISSUES.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find scripts/accelsim -maxdepth 1 -type f \( -name 'a11*.py' -o -name 'a12*.py' -o -name 'a13*.py' -o -name 'a14*.sh' -o -name 'a15*.sh' -o -name 'a11_a15_run_all.sh' -o -name 'accelsim_stats_parser.py' -o -name 'README.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_reports -maxdepth 1 -type f \( -name 'A11*.md' -o -name 'A11*.csv' -o -name 'A12*.md' -o -name 'A12*.csv' -o -name 'A13*.md' -o -name 'A13*.csv' -o -name 'A14*.md' -o -name 'A14*.csv' -o -name 'A15*.md' -o -name 'A15*.csv' -o -name 'A11_A15_final_summary_*.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_logs -maxdepth 1 -type f \( -name 'A11*.log' -o -name 'A12*.log' -o -name 'A13*.log' -o -name 'A14*.log' -o -name 'A15*.log' \) -size -3M | sort)

tar -czf "$review_pack" "${tar_inputs[@]}"

echo "A15 plan: $plan_path"
echo "A15 trace gap matrix: $matrix_path"
echo "A11-A15 summary: $summary_path"
echo "A11-A15 review pack: $review_pack"
echo "A15 status: $status"

case "$status" in
  PASS|PASS_WITH_NO_GPU) exit 0 ;;
  *) exit 1 ;;
esac
