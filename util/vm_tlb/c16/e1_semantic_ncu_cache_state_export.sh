#!/usr/bin/env bash
set -euo pipefail

OUT=/data/c16/e1_semantic_ncu_cache_state_repair_v1
NCU=/usr/local/cuda-12.8/bin/ncu

export_report() {
  local point_id=$1
  "$NCU" --import "$OUT/reports/$point_id.ncu-rep" --csv --page raw --print-units base \
    > "$OUT/reports/$point_id.base.csv"
  "$NCU" --import "$OUT/reports/$point_id.ncu-rep" --csv --page session \
    > "$OUT/reports/$point_id.session.csv"
}

export_report M1_RAW
export_report M1_AWQ
export_report M256_RAW
export_report M256_AWQ

printf 'PASS\n' > "$OUT/EXPORT_COMPLETE"
