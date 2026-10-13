#!/usr/bin/env bash
set -euo pipefail
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r27r3-numeric-attribution-capacity-109-v1
ROOT=/data/c16/awma/r27r3_numeric_attribution_109_v1_20261013
REMOTE=/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r27r3_numeric_attribution_109_v1_20261013
PY=/data/c16/awma/cce_zero_init_removal_109_v1_20260930/env/bin/python
cd "$WT"
export PYTHONDONTWRITEBYTECODE=1
"$PY" util/vm_tlb/awma/r27r3_numeric_attribution/finalize.py --mode prepare --repo "$WT" --root "$ROOT" --remote "$REMOTE"
ssh hrl174new "test ! -e '$REMOTE' && mkdir -p '$REMOTE'"
scp -q -r "$ROOT/raw" "$ROOT/logs" "$ROOT/receipts" "$ROOT/source" "$ROOT/r27r3_compact_publication.tgz" "$ROOT/R27R3_PUBLICATION_MANIFEST.tsv" "hrl174new:$REMOTE/"
ssh hrl174new "set -euo pipefail; cd '$REMOTE'; tail -n +2 R27R3_PUBLICATION_MANIFEST.tsv | awk -F '\t' '{print \$3\"  \"\$1}' | sha256sum -c - > MANIFEST_VERIFY.txt; wc -l MANIFEST_VERIFY.txt; sha256sum r27r3_compact_publication.tgz R27R3_PUBLICATION_MANIFEST.tsv"
COUNT=$(tail -n +2 "$ROOT/R27R3_PUBLICATION_MANIFEST.tsv" | wc -l)
"$PY" util/vm_tlb/awma/r27r3_numeric_attribution/finalize.py --mode close --repo "$WT" --root "$ROOT" --remote "$REMOTE" --verified-count "$COUNT"
PACK="$WT/docs/vm_tlb/review_packs/AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1"
ssh hrl174new "mkdir '$REMOTE/review_pack'"
scp -q "$PACK"/* "hrl174new:$REMOTE/review_pack/"
ssh hrl174new "set -euo pipefail; cd '$REMOTE/review_pack'; sha256sum -c SHA256SUMS > ../REVIEW_PACK_VERIFY.txt; wc -l ../REVIEW_PACK_VERIFY.txt; sha256sum SHA256SUMS"
