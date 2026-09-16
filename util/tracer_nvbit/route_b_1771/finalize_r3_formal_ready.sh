#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
run=C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9
stage=/data/c16/capture/staging/$run
ready=/data/c16/capture/ready
cd "$repo/util/vm_tlb/c16/data_plane"
/data/c16/env/c16-py310/bin/python finalize_capture.py --staging "$stage" --ready "$ready" --manifest "$stage/RUN_MANIFEST.json" --run-id "$run"
