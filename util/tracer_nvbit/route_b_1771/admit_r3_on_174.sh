#!/usr/bin/env bash
set -euo pipefail
run=C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
root=/root/share/mnt164/huangrulin/c16_ai_workload
wt=/root/workspace/awma-hotfix-admit
receipt="$root/reports/receiver_receipts/$run.VERIFICATION.json"
admission="$root/reports/receiver_receipts/$run.ADMISSION.json"
ssh hrl174new "set -euo pipefail; cd '$wt/util/vm_tlb/c16/data_plane'; python3 verify_capture.py --root '$root' --run-id '$run' --output '$receipt'; python3 admit_capture.py --root '$root' --verification-receipt '$receipt' --output '$admission'; python3 write_transfer_ack.py --root '$root' --admission-receipt '$admission'; sha256sum '$receipt' '$admission' '$root/reports/transfer_acks/$run.TRANSFER_ACK.json'"
