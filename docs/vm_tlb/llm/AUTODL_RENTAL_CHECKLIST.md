# Route-E AutoDL rental checklist

Status: `USER_CONFIRMED` availability snapshot from 2026-09-02 only; recheck
every item immediately before paying. No host ID is frozen.

- Select one physical host with at least four idle GPUs, then allocate all four
  in one instance. Do not join separate hosts.
- All selected GPUs must be the same model and `compute_cap=8.6` (SM86).
  RTX 3080 Ti 12 GiB is acceptable. RTX 3090 24 GiB is helpful headroom, not a
  requirement.
- Confirm at least 12 GiB per GPU, adequate host RAM for four Python ranks
  (target 64 GiB or more), and SSH plus a copy-back path.
- Ensure at least 500 GiB initially free or immediately expandable local
  storage; substantially more is preferable when inexpensive. Preserve the
  host until archive and destination checksums match.
- Record OS/image, `nvidia-smi -L`, full `nvidia-smi`, driver, CPU/RAM, disk,
  network, Framework SHA, and visible GPU list. A web page's CUDA 13.x label is
  not approval to use CUDA 13.x for this project.
- Run `host_preflight.py` before installing/building, then the checksum
  bootstrap, generic smoke, and `capture_ready_preflight.py`. All must pass
  before any Llama download or formal trace.

The prior page showed multi-3080-Ti hosts with 5/8 or 6/8 idle GPUs and roughly
1.6–2 TB expandable storage. This is a feasibility observation, not an
availability promise.
