#!/usr/bin/env bash
set -euo pipefail
remote=/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_target_selection_v1
local=/data/c16/awma/qwen25_s2_kernel_target_selection_v1
mkdir -p "$local"
ssh hrl174new "cd '$remote'; find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS"
for f in PREFILL_GEMM_SUBFAMILIES.tsv DECODE_GEMV_SUBFAMILIES.tsv DECODE_FLASH_SUBFAMILIES.tsv PREFILL_FLASH_10_OCCURRENCES.tsv TARGET_CANDIDATES.tsv NATIVE_TARGET_ALIGNMENT.md TARGET_SELECTION_RATIONALE.md SHA256SUMS; do
 scp "hrl174new:$remote/$f" "$local/"
done
scp -r "hrl174new:$remote/candidate_targets" "$local/"
find "$local" -maxdepth 2 -type f ! -name LOCAL_SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$local/LOCAL_SHA256SUMS"
ssh hrl174new "cd '$remote'; sha256sum -c SHA256SUMS" > "$local/NODE164_VERIFY.stdout" 2> "$local/NODE164_VERIFY.stderr"
grep -q 'OK' "$local/NODE164_VERIFY.stdout"
sha256sum "$local/NODE164_VERIFY.stdout" "$local/NODE164_VERIFY.stderr" > "$local/NODE164_VERIFY_SHA256SUMS"
