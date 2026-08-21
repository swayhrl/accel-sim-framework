#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
gpgpusim_root="${C2P_GPGPUSIM_ROOT:-$repo_root/../gpgpu-sim-c2p-cache}"
cacti_src="$gpgpusim_root/src/accelwattch/cacti"
out_dir="${1:-$script_dir/results/cacti_snapshot_proxy}"
build_root="${2:-$out_dir/build}"

[[ -f "$cacti_src/cacti.mk" ]] || {
  echo "error: C2P_GPGPUSIM_ROOT must contain AccelWattch CACTI: $gpgpusim_root" >&2
  exit 2
}
mkdir -p "$out_dir" "$build_root/accelwattch/cacti"
make -C "$cacti_src" -f cacti.mk SIM_OBJ_FILES_DIR="$build_root" -j8

# One Snapshot copy is 5120 x 64 bits = 40 KiB. Model it as a 64-bank,
# 8-byte-row RAM. Four physical copies are reported as a separate scaling.
sed \
  -e 's/^-size (bytes) 1073741824$/-size (bytes) 40960/' \
  -e 's/^-block size (bytes) 64$/-block size (bytes) 8/' \
  -e 's/^-associativity 8$/-associativity 1/' \
  -e 's/^-UCA bank count 1$/-UCA bank count 64/' \
  -e 's/^-output\/input bus width 512$/-output\/input bus width 64/' \
  -e 's@^-cache type "cache"$@//-cache type "cache"\n-cache type "ram"@' \
  -e 's@^-tag size (b) "default"$@-tag size (b) 0@' \
  -e 's/^-Add ECC - "true"$/-Add ECC - "false"/' \
  "$cacti_src/cache.cfg" > "$out_dir/snapshot_matrix_40KiB_64bank.cfg"

"$build_root/accelwattch/cacti/cacti" \
  -infile "$out_dir/snapshot_matrix_40KiB_64bank.cfg" \
  > "$out_dir/snapshot_matrix_40KiB_64bank.out"

rg -q 'Data array: Area' "$out_dir/snapshot_matrix_40KiB_64bank.out"
rg -n 'Access time|Cycle time|dynamic read energy/access|Data array: Area' \
  "$out_dir/snapshot_matrix_40KiB_64bank.out" > "$out_dir/summary.txt"
printf 'PASS cacti_snapshot_proxy result_dir=%s\n' "$out_dir"
