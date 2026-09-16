#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
run=C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
ready=/data/c16/capture/ready/$run
dest=/root/share/mnt164/huangrulin/c16_ai_workload
cd "$repo/util/vm_tlb/c16/data_plane"
/data/c16/env/c16-py310/bin/python publish_capture.py --ssh-alias hrl174new --destination-root "$dest" --run-id "$run" --source "$ready" --dry-run
