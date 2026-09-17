#!/usr/bin/env bash
set -euo pipefail
src=/data/c16/awma/qwen25_s2_kernel_census_20260917T101100Z
dest=/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z
/data/c16/env/c16-py310/bin/python /tmp/prepare_census_durable_payload.py > "$src/durable_destination.txt"
rsync -r --partial --append-verify --protect-args --no-owner --no-group --no-perms --omit-dir-times "$src/" "hrl174new:$dest/" > "$src/archive_rsync.stdout" 2> "$src/archive_rsync.stderr"
sha256sum "$src/RAW_DATA_INDEX.tsv" "$src/archive_rsync.stdout" "$src/archive_rsync.stderr" > "$src/ARCHIVE_TRANSFER_SHA256SUMS"
ssh hrl174new "set -euo pipefail; cd '$dest'; while IFS=\$'\\t' read -r rel size hash final; do test \"\$rel\" = relative_path && continue; test \"\$(stat -c %s \"\$rel\")\" = \"\$size\"; test \"\$(sha256sum \"\$rel\" | awk '{print \$1}')\" = \"\$hash\"; done < RAW_DATA_INDEX.tsv; echo NODE164_CENSUS_HASH_VERIFY_PASS"
