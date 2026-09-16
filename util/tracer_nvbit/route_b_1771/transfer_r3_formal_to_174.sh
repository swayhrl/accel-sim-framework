#!/usr/bin/env bash
set -euo pipefail
run=C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
source=/data/c16/capture/ready/$run
dest=/root/share/mnt164/huangrulin/c16_ai_workload/inbox/$run.partial/
receipt=/data/c16/capture/transfer_receipts/$run
mkdir -p "$receipt"
printf 'rsync -r --partial --append-verify --protect-args --no-owner --no-group --no-perms --omit-dir-times %s hrl174new:%s\n' "$source/" "$dest" > "$receipt/transfer_command.txt"
rsync -r --partial --append-verify --protect-args --no-owner --no-group --no-perms --omit-dir-times "$source/" "hrl174new:$dest" > "$receipt/rsync.stdout" 2> "$receipt/rsync.stderr"
sha256sum "$receipt/transfer_command.txt" "$receipt/rsync.stdout" "$receipt/rsync.stderr" > "$receipt/SHA256SUMS"
echo TRANSFER_COPY_PASS
