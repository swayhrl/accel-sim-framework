#!/usr/bin/env bash
# Strict, auditable closeout for the C2P paper16 campaign.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/finalize_c2p_paper16.sh \
  --results-root DIR --l2-fast-root DIR --ccd-metrics-root DIR \
  --sweep-root DIR --analysis-dir DIR --figures-dir DIR --report FILE \
  [--queue-sensitivity-root DIR] \
  [--supplemental-sweep-root DIR] \
  [--supplemental-results-root DIR] \
  [--ccd-mode-root DIR] \
  [--supplemental-l2-fast-root DIR] \
  [--supplemental-ccd-metrics-root DIR] [--python PYTHON]

Run the strict paper16 evidence pipeline in dependency order:
  1. seven-mode / L2=50 / CCD analysis and mode-contract audit;
  2. default m5120 C2P equivalence across replay binary revisions;
  3. complete Figure-13 m/k analysis;
  4. strict Figure 10--14 rendering;
  5. optional strict finite-queue diagnosis and final directional report.

Every result root is an input.  Supplemental roots only fill missing modes;
the canonical root remains authoritative whenever it has a completed run.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON:-python3}"
results_root=""; l2_fast_root=""; ccd_metrics_root=""; sweep_root=""
analysis_dir=""; figures_dir=""; report=""
queue_sensitivity_root=""
ccd_mode_root=""
supplemental_results=(); supplemental_l2=(); supplemental_ccd=(); supplemental_sweep=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --results-root) results_root="$2"; shift 2 ;;
    --l2-fast-root) l2_fast_root="$2"; shift 2 ;;
    --ccd-metrics-root) ccd_metrics_root="$2"; shift 2 ;;
    --sweep-root) sweep_root="$2"; shift 2 ;;
    --analysis-dir) analysis_dir="$2"; shift 2 ;;
    --figures-dir) figures_dir="$2"; shift 2 ;;
    --report) report="$2"; shift 2 ;;
    --queue-sensitivity-root) queue_sensitivity_root="$2"; shift 2 ;;
    --ccd-mode-root) ccd_mode_root="$2"; shift 2 ;;
    --supplemental-results-root) supplemental_results+=("$2"); shift 2 ;;
    --supplemental-l2-fast-root) supplemental_l2+=("$2"); shift 2 ;;
    --supplemental-ccd-metrics-root) supplemental_ccd+=("$2"); shift 2 ;;
    --supplemental-sweep-root) supplemental_sweep+=("$2"); shift 2 ;;
    --python) python_bin="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

for value in "$results_root" "$l2_fast_root" "$ccd_metrics_root" "$sweep_root"; do
  [[ -n "$value" && -d "$value" ]] || {
    echo "error: every input root must exist" >&2; exit 2;
  }
done
[[ -n "$analysis_dir" && -n "$figures_dir" && -n "$report" ]] || {
  echo "error: --analysis-dir, --figures-dir, and --report are required" >&2; exit 2;
}
if [[ -n "$ccd_mode_root" && ! -d "$ccd_mode_root" ]]; then
  echo "error: --ccd-mode-root must exist" >&2; exit 2;
fi

analysis_args=(--results-root "$results_root" --l2-fast-root "$l2_fast_root"
               --ccd-metrics-root "$ccd_metrics_root" --out-dir "$analysis_dir" --strict)
[[ -n "$ccd_mode_root" ]] && analysis_args+=(--mode-override-root "ccd=$ccd_mode_root")
for root in "${supplemental_results[@]}"; do analysis_args+=(--supplemental-results-root "$root"); done
for root in "${supplemental_l2[@]}"; do analysis_args+=(--supplemental-l2-fast-root "$root"); done
for root in "${supplemental_ccd[@]}"; do analysis_args+=(--supplemental-ccd-metrics-root "$root"); done

"$python_bin" "$repo_root/scripts/analyze_c2p_paper16.py" "${analysis_args[@]}"
equivalence_args=(--primary-root "$results_root" --reference-root "$sweep_root"
                  --out "$analysis_dir/default_c2p_equivalence.csv" --strict)
for root in "${supplemental_results[@]}"; do
  equivalence_args+=(--supplemental-primary-root "$root")
done
for root in "${supplemental_sweep[@]}"; do
  equivalence_args+=(--supplemental-reference-root "$root")
done
"$python_bin" "$repo_root/scripts/check_c2p_default_equivalence.py" \
  "${equivalence_args[@]}"
fp_args=(--sweep-root "$sweep_root" --paper16-analysis "$analysis_dir"
         --out-dir "$analysis_dir" --strict)
for root in "${supplemental_sweep[@]}"; do fp_args+=(--supplemental-sweep-root "$root"); done
"$python_bin" "$repo_root/scripts/analyze_c2p_fp_sweep.py" "${fp_args[@]}"
report_args=(--analysis-dir "$analysis_dir" --figures-dir "$figures_dir" --report "$report")
if [[ -n "$queue_sensitivity_root" ]]; then
  [[ -d "$queue_sensitivity_root" ]] || {
    echo "error: --queue-sensitivity-root must exist" >&2; exit 2;
  }
  queue_analysis="$analysis_dir/queue-sensitivity"
  "$python_bin" "$repo_root/scripts/analyze_c2p_queue_sensitivity.py" \
    --default-run "$results_root/btree/c2p" \
    --sensitivity-root "$queue_sensitivity_root" \
    --out-dir "$queue_analysis" --strict
  report_args+=(--queue-sensitivity-csv "$queue_analysis/queue_sensitivity.csv")
fi
"$python_bin" "$repo_root/scripts/plot_c2p_paper_figures.py" \
  --analysis-dir "$analysis_dir" --out-dir "$figures_dir" --strict
"$python_bin" "$repo_root/scripts/render_c2p_paper16_report.py" "${report_args[@]}"

printf 'PASS strict C2P paper16 closeout: analysis=%s figures=%s report=%s\n' \
  "$analysis_dir" "$figures_dir" "$report"
