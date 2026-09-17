#!/usr/bin/env bash
set -euo pipefail
wt=/home/huangrulin/workspace/worktrees/accel-sim-awma-target-selection-v1
index="$wt/docs/vm_tlb/review_packs/AWMA_QWEN25_S2_KERNEL_CENSUS_109_V1/ALL_KERNEL_LAUNCHES_INDEX.json"
receipt="$wt/docs/vm_tlb/review_packs/AWMA_QWEN25_S2_KERNEL_CENSUS_109_V1/RUN_RECEIPT.json"
expected=$(/data/c16/env/c16-py310/bin/python -c "import json;print(json.load(open('$index'))['sha256'])")
remote=/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/analysis/ALL_KERNEL_LAUNCHES.tsv
actual=$(ssh hrl174new "sha256sum '$remote' | awk '{print \$1}'")
test "$actual" = "$expected"
/data/c16/env/c16-py310/bin/python - <<PY
import json
r=json.load(open('$receipt'))
assert r['kernel_launches_total']==34677
assert r['inference_kernel_launches']==34072
assert len(r['nvtx_ranges'])==33
assert r['nvtx_ranges'][0]['phase']=='PREFILL'
assert sum(x['phase']=='DECODE' for x in r['nvtx_ranges'])==32
print('D0_WORKLOAD_AND_NVTX_PASS')
PY
printf 'inventory_path=%s\ninventory_sha256=%s\nworkload_nvtx_identity=PASS\n' "$remote" "$actual" > /tmp/d0_selection_receipt.txt
cat /tmp/d0_selection_receipt.txt
