#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
run=C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
root=/root/share/mnt164/huangrulin/c16_ai_workload
ready=/data/c16/capture/ready
transferred=/data/c16/capture/transferred
receipt=/data/c16/capture/transfer_receipts/$run
mkdir -p "$receipt" "$transferred"
scp "hrl174new:$root/reports/transfer_acks/$run.TRANSFER_ACK.json" "$receipt/TRANSFER_ACK.json"
scp "hrl174new:$root/reports/receiver_receipts/$run.VERIFICATION.json" "$receipt/REMOTE_VERIFICATION.json"
scp "hrl174new:$root/reports/receiver_receipts/$run.ADMISSION.json" "$receipt/REMOTE_ADMISSION.json"
manifest_sha=$(sha256sum "$ready/$run/RUN_MANIFEST.json" | awk '{print $1}')
cd "$repo/util/vm_tlb/c16/data_plane"
/data/c16/env/c16-py310/bin/python verify_remote_ack.py --ack "$receipt/TRANSFER_ACK.json" --run-id "$run" --manifest-sha "$manifest_sha" --destination "$root/raw/$run" --file-count 20 --total-bytes 121352515 --ready "$ready" --transferred "$transferred" > "$receipt/ACK_VERIFY.stdout" 2> "$receipt/ACK_VERIFY.stderr"
sha256sum "$receipt"/* > "$receipt/SHA256SUMS"
echo ACK_VERIFY_AND_TRANSITION_PASS
