# Codex start here — V2B destination runtime bootstrap

Run this task on the new/destination Docker.

Branch:

`hrl/c16-ai-workload-2239-runtime-bootstrap-v2b`

Read `HANDOFF.md` in this directory completely before acting.

First gate: prove whether this container actually exposes the intended RTX4080. If `/dev/nvidia*`/`nvidia-smi` device exposure is absent, do not install CUDA/PyTorch/transformers/NVBit/NCU. Produce the required host enablement request, commit, push, stop.

If GPU exposure is present, proceed only with bounded userspace runtime/toolchain admission as authorized by the handoff. Do not run Llama, model NVBit, or model NCU.

Commit, push, stop, and report the V2B decision.