#!/usr/bin/env bash
set -euo pipefail

OUT=/data/c16/e1_natural_reuse_residency_v1
NCU=/usr/local/cuda-12.8/bin/ncu

while IFS= read -r -d '' report; do
  stem=${report%.ncu-rep}
  "$NCU" --import "$report" --csv --page raw --print-units base > "${stem}.base.csv"
  "$NCU" --import "$report" --csv --page session > "${stem}.session.csv"
done < <(find "$OUT/ncu" -type f -name '*.ncu-rep' -print0 | sort -z)

printf 'PASS\n' > "$OUT/ncu/EXPORT_COMPLETE"
