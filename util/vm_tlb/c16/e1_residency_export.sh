#!/usr/bin/env bash
set -euo pipefail

OUT=/data/c16/e1_residency_intervention_v1
NCU=/usr/local/cuda-12.8/bin/ncu

for report in "$OUT"/ncu/reports/*.ncu-rep; do
  stem=${report%.ncu-rep}
  "$NCU" --import "$report" --csv --page raw --print-units base > "${stem}.base.csv"
  "$NCU" --import "$report" --csv --page session > "${stem}.session.csv"
done

printf 'PASS\n' > "$OUT/ncu/EXPORT_COMPLETE"
