#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
test_dir=$(mktemp -d "${TMPDIR:-/tmp}/c16_e1_mapper_test.XXXXXX")
trap 'rm -rf -- "$test_dir"' EXIT

export C16_ACCEPTED_MAPPER_BUILD_DIR="$test_dir/build"
binary=$($script_dir/build_accepted_l2_mapper.sh)

"$binary" --self-test >"$test_dir/self_test.out" 2>"$test_dir/self_test.err"
grep -Fx $'ACCEPTED_L2_MAPPER_CANARY_PASS\t9' "$test_dir/self_test.out"
grep -Fx 'accepted_core_sha=a2322069b9701597db7019080b5b54d29518e3a2' \
  "$test_dir/self_test.err"
grep -Fx 'accepted_config_sha256=de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8' \
  "$test_dir/self_test.err"

printf '%s\n' \
  '0x7ea94e000000' \
  '139264432209920 # L14 midpoint, decimal' \
  '0x7ea7e005ff80' |
  "$binary" map >"$test_dir/batch.out" 2>"$test_dir/batch.err"

diff -u <(printf '%s\n' \
  $'line_address_hex\tsubpartition\tset_index' \
  $'0x7ea94e000000\t0\t1336' \
  $'0x7ea907030000\t0\t1148' \
  $'0x7ea7e005ff80\t15\t1855') \
  "$test_dir/batch.out"

if printf '%s\n' '-1' | "$binary" map --no-header >"$test_dir/bad.out" 2>"$test_dir/bad.err"; then
  echo "negative address unexpectedly accepted" >&2
  exit 1
fi
grep -F 'invalid address at input line 1: -1' "$test_dir/bad.err"

perl -e 'print pack("Q<*", 0x7ea7de000000, 0x7ea94e000000)' \
  >"$test_dir/lines.u64le"
"$binary" map --input-lines-u64 "$test_dir/lines.u64le" \
  --output-tsv "$test_dir/lines.tsv" 2>"$test_dir/file_mode.err"
diff -u <(printf '%s\n' \
  $'line_address_hex\tsubpartition\tset_index' \
  $'0x7ea7de000000\t0\t1912' \
  $'0x7ea94e000000\t0\t1336') \
  "$test_dir/lines.tsv"

printf '\200' >"$test_dir/truncated.u64le"
if "$binary" map --input-lines-u64 "$test_dir/truncated.u64le" \
  --output-tsv "$test_dir/truncated.tsv" >"$test_dir/truncated.out" \
  2>"$test_dir/truncated.err"; then
  echo "truncated u64 input unexpectedly accepted" >&2
  exit 1
fi
grep -F 'truncated input-lines-u64 record' "$test_dir/truncated.err"

perl -e 'print pack("Q<", 0x7ea94e000001)' >"$test_dir/unaligned.u64le"
if "$binary" map --input-lines-u64 "$test_dir/unaligned.u64le" \
  --output-tsv "$test_dir/unaligned.tsv" >"$test_dir/unaligned.out" \
  2>"$test_dir/unaligned.err"; then
  echo "unaligned u64 input unexpectedly accepted" >&2
  exit 1
fi
grep -F 'unaligned 128B line address at record 0' "$test_dir/unaligned.err"

perl -e 'print pack("Q<*", 0x7ea94e000000, 0x7ea7de000000)' \
  >"$test_dir/descending.u64le"
if "$binary" map --input-lines-u64 "$test_dir/descending.u64le" \
  --output-tsv "$test_dir/descending.tsv" >"$test_dir/descending.out" \
  2>"$test_dir/descending.err"; then
  echo "descending u64 input unexpectedly accepted" >&2
  exit 1
fi
grep -F 'input-lines-u64 is not sorted at record 1' \
  "$test_dir/descending.err"

"$binary" --provenance >"$test_dir/provenance.out"
grep -Fx 'accepted_mapper_schema=C16_E1_ACCEPTED_L2_MAPPER_V1' \
  "$test_dir/provenance.out"

echo C16_E1_ACCEPTED_L2_MAPPER_TEST_PASS
