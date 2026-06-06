#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
main_log=".local_logs/A6_clean_baseline_rerun_${ts}.log"
build_log=".local_logs/A6_build_${ts}.log"
report_path=".local_reports/A6_clean_baseline_summary_${ts}.md"
review_pack="review_packs/A6_CLEAN_BASELINE_RERUN_review_pack_${ts}.tar.gz"
dirty_scan_path=".local_reports/A6_dirty_marker_scan_${ts}.log"
build_string_excerpt_path=".local_reports/A6_build_string_excerpts_${ts}.log"

status="PASS"
blocker="none"
build_result="not_run"
build_command_used="not_run"
binary_status="not_checked"
ldd_missing="not_checked"
trace_root=""
trace_root_source="not_found"
trace_kernel_count="0"
run_name_a2="A6_pretrace_clean_${ts}"
run_name_a4="A6_suite_clean_${ts}"
a2_result="not_run"
a4_result="not_run"
a2_report=""
a4_report=""
a2_stats=""
a4_stats=""
dirty_marker_found="not_checked"
baseline_found="not_checked"
git_status_start=""
git_status_end=""
baseline_commit=""
baseline_short=""
branch=""

exec > >(tee "$main_log") 2>&1

run_cmd() {
  echo
  echo "+ $*"
  "$@"
}

latest_matching_file() {
  local pattern="$1"
  ls -t $pattern 2>/dev/null | head -1 || true
}

report_status() {
  local file="$1"
  if [ -n "$file" ] && [ -f "$file" ]; then
    sed -n 's/^- Status: //p' "$file" | head -1
  else
    echo "MISSING"
  fi
}

extract_stats_from_report() {
  local file="$1"
  if [ -n "$file" ] && [ -f "$file" ]; then
    sed -n 's/^- Stats CSV: `\(.*\)`/\1/p' "$file" | head -1
  fi
}

candidate_trace_roots_from_reports() {
  sed -n 's/^- Trace root: `\(.*\)`/\1/p' .local_reports/A2*.md .local_reports/A4*.md 2>/dev/null | sed '/^$/d'
}

candidate_trace_roots_from_kernels() {
  find .local_traces hw_run . -type f -name kernelslist.g 2>/dev/null | sort | while read -r kernels_file; do
    python3 - "$kernels_file" <<'PY'
import os, sys
p = os.path.abspath(sys.argv[1])
for _ in range(4):
    p = os.path.dirname(p)
print(p)
PY
  done
}

select_trace_root() {
  local candidates=()
  local c
  if [ -n "${ACCELSIM_TRACE_ROOT:-}" ]; then
    candidates+=("$ACCELSIM_TRACE_ROOT")
  fi
  while IFS= read -r c; do candidates+=("$c"); done < <(candidate_trace_roots_from_reports)
  while IFS= read -r c; do candidates+=("$c"); done < <(candidate_trace_roots_from_kernels)

  echo "Trace root candidates:"
  printf '  %s\n' "${candidates[@]:-<none>}"

  for c in "${candidates[@]:-}"; do
    [ -n "$c" ] || continue
    if [ -d "$c" ] && find "$c" -type f -name kernelslist.g 2>/dev/null | grep -q .; then
      trace_root="$(cd "$c" && pwd)"
      if [ -n "${ACCELSIM_TRACE_ROOT:-}" ] && [ "$c" = "$ACCELSIM_TRACE_ROOT" ]; then
        trace_root_source="ACCELSIM_TRACE_ROOT"
      else
        trace_root_source="discovered"
      fi
      trace_kernel_count="$(find "$trace_root" -type f -name kernelslist.g 2>/dev/null | wc -l | tr -d ' ')"
      return 0
    fi
  done
  return 1
}

write_report() {
  local end_epoch end_iso wall_clock
  end_epoch="$(date +%s)"
  end_iso="$(date -Iseconds)"
  wall_clock="$((end_epoch - start_epoch))"
  git_status_end="$(git status --short)"

  cat > "$report_path" <<EOF
# A6 Clean Baseline Rerun

## Status

$status

## Baseline commit

- Branch: \`$branch\`
- Commit: \`$baseline_commit\`
- Short commit: \`$baseline_short\`
- Git status at start:

\`\`\`
$git_status_start
\`\`\`

- Git status at end:

\`\`\`
$git_status_end
\`\`\`

## Timing

- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock

## Environment

- CUDA_INSTALL_PATH: \`${CUDA_INSTALL_PATH:-}\`
- ACCELSIM_ROOT: \`${ACCELSIM_ROOT:-}\`
- GPGPUSIM_ROOT: \`${GPGPUSIM_ROOT:-}\`

\`\`\`
$(nvcc --version 2>&1 | sed -n '1,4p')
$(gcc --version 2>&1 | sed -n '1p')
$(g++ --version 2>&1 | sed -n '1p')
$(cmake --version 2>&1 | sed -n '1p')
$(python3 --version 2>&1)
\`\`\`

## Build

- Command used: \`$build_command_used\`
- Build result: $build_result
- Binary: \`gpu-simulator/bin/release/accel-sim.out\`
- Binary status: $binary_status
- Binary timestamp: \`$(stat -c '%y' gpu-simulator/bin/release/accel-sim.out 2>/dev/null || echo missing)\`
- ldd missing libraries: $ldd_missing
- Build log: \`$build_log\`

## Trace root

- Trace root: \`${trace_root:-}\`
- How selected: $trace_root_source
- kernelslist.g count: $trace_kernel_count

## Smoke reruns

### A2 style pre-trace smoke

- Run name: \`$run_name_a2\`
- Result: $a2_result
- Report: \`$a2_report\`
- Stats CSV: \`$a2_stats\`

### A4 style smoke suite

- Run name: \`$run_name_a4\`
- Result: $a4_result
- Report: \`$a4_report\`
- Stats CSV: \`$a4_stats\`

## Build string validation

- Dirty or modified marker found: $dirty_marker_found
- Baseline commit found in logs or stats: $baseline_found
- Dirty marker scan: \`$dirty_scan_path\`
- Build string excerpts: \`$build_string_excerpt_path\`

### Excerpts

\`\`\`
$(sed -n '1,120p' "$build_string_excerpt_path" 2>/dev/null)
\`\`\`

### Dirty marker grep

\`\`\`
$(sed -n '1,120p' "$dirty_scan_path" 2>/dev/null)
\`\`\`

## Limitations

- This is a minimal smoke rerun, not a full Rodinia benchmark campaign.
- A3/NVBit tracer is intentionally not validated by A6.
- A6 does not download traces; it reuses an existing trace root.
- Current version makefiles always include the token \`_modified_\` in build-string format, even for a zero diff count. This script reports that honestly.

## Review pack

- Path: \`$review_pack\`
- Main log: \`$main_log\`
- Blocker: $blocker
EOF
}

create_review_pack() {
  local tar_inputs=()
  for f in \
    docs/accelsim_bringup/A6_CLEAN_BASELINE_RERUN.md \
    docs/accelsim_bringup/A6_BASELINE_REPORT_TEMPLATE.md \
    docs/accelsim_bringup/CODEX_PROMPT_A6.md \
    scripts/accelsim/a6_clean_baseline_rerun.sh \
    scripts/accelsim/accelsim_env.sh \
    scripts/accelsim/a2_pretrace_smoke.sh \
    scripts/accelsim/a4_run_smoke_suite.sh; do
    [ -f "$f" ] && tar_inputs+=("$f")
  done
  while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_reports -maxdepth 1 -type f \( -name 'A6*.md' -o -name 'A6*_stats.csv' -o -name 'A6*.log' \) | sort)
  while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_logs -maxdepth 1 -type f -name 'A6*.log' -size -3M | sort)
  [ -n "$a2_report" ] && [ -f "$a2_report" ] && tar_inputs+=("$a2_report")
  [ -n "$a4_report" ] && [ -f "$a4_report" ] && tar_inputs+=("$a4_report")
  [ -n "$a2_stats" ] && [ -f "$a2_stats" ] && tar_inputs+=("$a2_stats")
  [ -n "$a4_stats" ] && [ -f "$a4_stats" ] && tar_inputs+=("$a4_stats")

  echo
  echo "+ tar -czf $review_pack ..."
  tar -czf "$review_pack" "${tar_inputs[@]}"
}

finish() {
  write_report
  create_review_pack
  echo
  echo "A6 status: $status"
  echo "Baseline commit: $baseline_commit"
  echo "A2 stats CSV: $a2_stats"
  echo "A4 stats CSV: $a4_stats"
  echo "A6 summary: $report_path"
  echo "Review pack: $review_pack"
  echo "Final git status --short:"
  git status --short

  case "$status" in
    PASS|PASS_NO_DIRTY_MARKER_COMMIT_NOT_FOUND|PARTIAL_BUILD_BINARY_EXISTS|BLOCKED_NO_TRACE) exit 0 ;;
    *) exit 1 ;;
  esac
}

echo "A6 clean baseline rerun"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a6_clean_baseline_rerun.sh"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
  finish
fi

branch="$(git branch --show-current)"
baseline_commit="$(git rev-parse HEAD)"
baseline_short="$(git rev-parse --short=12 HEAD)"
git_status_start="$(git status --short)"

echo "Branch: $branch"
echo "Baseline commit: $baseline_commit"
echo "Baseline short: $baseline_short"
echo
echo "git status --short at start:"
printf '%s\n' "$git_status_start"

echo
echo "Toolchain:"
nvcc --version || true
gcc --version | sed -n '1,2p' || true
g++ --version | sed -n '1,2p' || true
cmake --version | sed -n '1,2p' || true
python3 --version || true

if [ -n "$git_status_start" ]; then
  status="FAILED_DIRTY_TREE"
  blocker="git status was not clean at A6 start"
  finish
fi

build_command_used="make -B -j$(nproc) -C ./gpu-simulator/"
echo
echo "+ $build_command_used"
if make -B "-j$(nproc)" -C ./gpu-simulator/ >"$build_log" 2>&1; then
  build_result="PASS_FORCE_REBUILD"
else
  echo "Forced rebuild failed; trying normal make fallback. See $build_log"
  build_command_used="make -j$(nproc) -C ./gpu-simulator/"
  {
    echo
    echo "==== normal make fallback ===="
  } >>"$build_log"
  if make "-j$(nproc)" -C ./gpu-simulator/ >>"$build_log" 2>&1; then
    build_result="PASS_NORMAL_MAKE_FALLBACK"
  else
    build_result="FAILED"
  fi
fi

if [ -x ./gpu-simulator/bin/release/accel-sim.out ]; then
  binary_status="EXECUTABLE"
else
  binary_status="MISSING_OR_NOT_EXECUTABLE"
fi

echo
echo "+ test -x ./gpu-simulator/bin/release/accel-sim.out"
test -x ./gpu-simulator/bin/release/accel-sim.out || true
echo
echo "+ file ./gpu-simulator/bin/release/accel-sim.out"
file ./gpu-simulator/bin/release/accel-sim.out || true
echo
echo "+ ldd ./gpu-simulator/bin/release/accel-sim.out"
ldd ./gpu-simulator/bin/release/accel-sim.out || true

if ldd ./gpu-simulator/bin/release/accel-sim.out 2>/dev/null | grep -q "not found"; then
  ldd_missing="YES"
else
  ldd_missing="NO"
fi

if [ "$build_result" = "FAILED" ]; then
  if [ "$binary_status" = "EXECUTABLE" ] && [ "$ldd_missing" = "NO" ]; then
    status="PARTIAL_BUILD_BINARY_EXISTS"
    blocker="force and normal make failed, but existing binary is executable and ldd clean"
  else
    status="FAILED_BUILD"
    blocker="build failed and no usable binary is available"
    finish
  fi
fi

if [ "$binary_status" != "EXECUTABLE" ] || [ "$ldd_missing" != "NO" ]; then
  status="FAILED_BINARY"
  blocker="binary missing/not executable or ldd has missing libraries"
  finish
fi

if ! select_trace_root; then
  status="BLOCKED_NO_TRACE"
  blocker="no usable trace root found; A6 does not download traces"
  dirty_marker_found="not_checked_no_trace"
  baseline_found="not_checked_no_trace"
  finish
fi

echo
echo "Selected trace root: $trace_root"
echo "Trace root source: $trace_root_source"
echo "kernelslist.g count: $trace_kernel_count"

echo
echo "+ ACCELSIM_TRACE_ROOT=$trace_root ACCELSIM_RUN_NAME=$run_name_a2 bash scripts/accelsim/a2_pretrace_smoke.sh"
if env -u ACCELSIM_CONFIG \
  ACCELSIM_TRACE_ROOT="$trace_root" \
  ACCELSIM_RUN_NAME="$run_name_a2" \
  ACCELSIM_A2_LAUNCH_MODE=direct \
  bash scripts/accelsim/a2_pretrace_smoke.sh; then
  a2_result="PASS"
else
  a2_result="FAILED"
  status="FAILED_A2_SMOKE"
  blocker="A2 style clean smoke failed"
fi
a2_report="$(latest_matching_file '.local_reports/A2_pretrace_smoke_*.md')"
a2_stats="$(extract_stats_from_report "$a2_report")"

if [ "$status" = "PASS" ] || [ "$status" = "PARTIAL_BUILD_BINARY_EXISTS" ]; then
  echo
  echo "+ ACCELSIM_TRACE_ROOT=$trace_root ACCELSIM_RUN_NAME=$run_name_a4 bash scripts/accelsim/a4_run_smoke_suite.sh"
  if env -u ACCELSIM_CONFIG \
    ACCELSIM_TRACE_ROOT="$trace_root" \
    ACCELSIM_RUN_NAME="$run_name_a4" \
    ACCELSIM_A4_LAUNCH_MODE=direct \
    bash scripts/accelsim/a4_run_smoke_suite.sh; then
    a4_result="PASS"
  else
    a4_result="FAILED"
    status="FAILED_A4_SMOKE"
    blocker="A4 style clean smoke failed"
  fi
  a4_report="$(latest_matching_file '.local_reports/A4_smoke_suite_*.md')"
  a4_stats="$(extract_stats_from_report "$a4_report")"
fi

scan_files=()
for f in "$main_log" "$build_log" "$a2_report" "$a4_report" "$a2_stats" "$a4_stats"; do
  [ -n "$f" ] && [ -f "$f" ] && scan_files+=("$f")
done

{
  echo "Files scanned:"
  printf '%s\n' "${scan_files[@]}"
  echo
  echo "Marker matches:"
  if ! grep -RinE '(_modified|modified|dirty)' "${scan_files[@]}" 2>/dev/null; then
    echo "NO_MATCHES"
  fi
} > "$dirty_scan_path"

{
  echo "Build string excerpts:"
  grep -RinE '(Accel-Sim-build|GPGPU-Sim-build|accelsim-commit|gpgpu-sim_git-commit)' "${scan_files[@]}" 2>/dev/null || true
} > "$build_string_excerpt_path"

if grep -qvE '^(Files scanned:|Marker matches:|NO_MATCHES|$)' "$dirty_scan_path"; then
  dirty_marker_found="YES"
else
  dirty_marker_found="NO"
fi

if grep -Riq "$baseline_short" "${scan_files[@]}" 2>/dev/null || grep -Riq "${baseline_commit:0:7}" "${scan_files[@]}" 2>/dev/null; then
  baseline_found="YES"
else
  baseline_found="NO"
fi

if [ "$status" = "PASS" ] || [ "$status" = "PARTIAL_BUILD_BINARY_EXISTS" ]; then
  if [ "$dirty_marker_found" = "YES" ]; then
    status="FAILED_DIRTY_BUILD_STRING"
    blocker="A6 logs/stats still contain dirty/modified marker in build string context"
  elif [ "$baseline_found" != "YES" ]; then
    status="PASS_NO_DIRTY_MARKER_COMMIT_NOT_FOUND"
    blocker="no dirty marker found, but baseline short commit was not found in logs/stats"
  fi
fi

finish
