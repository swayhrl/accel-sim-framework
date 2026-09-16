#!/usr/bin/env bash
set -euo pipefail
bin=/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b
out=/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/negatives
mkdir -p "$out"
for opcode in LDG.E.32 LDGSTS.E.BYPASS.LTC128B.128; do
  safe=$(printf '%s' "$opcode" | tr '. ' '__')
  cat > "$out/$safe.traceg" <<EOF
-kernel name = negative_$safe
-kernel id = 1
-grid dim = (1,1,1)
-block dim = (32,1,1)
-shmem = 0
-nregs = 8
-binary version = 89
-cuda stream id = 0
-shmem base_addr = 0x0
-local mem base_addr = 0x0
-nvbit version = 1.7.7.1
-accelsim tracer version = 5
-enable lineinfo = 0

#traces format = x

#BEGIN_TB
thread block = 0,0,0
warp = 0
insts = 1
0000 ffffffff 0 $opcode 0 0 0
#END_TB
EOF
  xz -zkf "$out/$safe.traceg"
  set +e
  "$bin" "$out/$safe.traceg.xz" > "$out/$safe.stdout" 2> "$out/$safe.stderr"
  rc=$?
  set -e
  printf '%s\n' "$rc" > "$out/$safe.returncode"
  test "$rc" -ne 0
  grep -q 'memory opcode has zero/missing width' "$out/$safe.stderr"
done
sha256sum "$out"/* > "$out/SHA256SUMS"
echo HOTFIX_MEMORY_NEGATIVES_PASS
