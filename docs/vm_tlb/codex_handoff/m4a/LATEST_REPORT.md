# M4A-C0 rented-host pilot report

Stage: `M4A_C0_RENTED_HOST_PILOT`

## PILOT_BLOCKED

P0–P4 passed on the rented qualifying host. P5 cannot proceed because the
remote environment has no Hugging Face credential with access to the frozen,
gated model revision `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.
The access probe returned `LocalTokenNotFoundError`; no token value was read or
logged. Consequently no Llama weights were downloaded, no TP4 model smoke was
run, and no Llama trace was collected.

The minimal action required to resume is to set a token that has accepted the
Llama 3.2 license and can read that exact revision in the remote execution
environment, e.g. `HF_TOKEN` for the AutoDL session. Do not put the token in a
repository file or handoff report.

Passed evidence:

- P1: one host, 4× RTX 3080 Ti 12 GiB, all SM86, 251 GiB RAM, 80 CPUs, and
  999 GiB initial free on `/root/autodl-tmp`.
- P2: Python 3.10.12, PyTorch `2.6.0+cu126` (`torch.version.cuda=12.6`),
  selected local CUDA 12.6.85 `nvcc`/`ptxas`, and all other locked package
  versions.
- P3: checksum-verified NVBit 1.7.6, explicit-toolchain build,
  capture-ready preflight, and generic injection→postprocess→archive chain.
- P4: real four-rank CUDA/Gloo synchronization; smoke had no injection on all
  ranks and trace had the reviewed tracer path only on rank 0.

The copy-backed evidence and gate-level details are in
`docs/vm_tlb/review_packs/M4A_RENTED_HOST_PILOT/`. No M4A-C Goal-mode action is
authorized by this blocked pilot result.
