# SUPERSEDED — DO NOT EXECUTE

The V2B runtime-bootstrap plan on this branch is superseded before execution.

Topology correction from the user:

- Docker `2239` is intentionally **CPU-only** for the C16 AI-workload program.
- The RTX4080 GPU execution node is `109`, not Docker `2239`.
- Therefore missing `/dev/nvidia*`, CUDA runtime, NVBit, and NCU inside `2239` are **not defects to repair**.
- Do not attempt GPU passthrough, CUDA/PyTorch/NVBit/NCU bootstrap, privileged container changes, or model execution in `2239` under this branch.

Long-term role split:

- `109`: GPU execution plane — Llama runs, bounded NVBit capture, NCU profiling, GPU-side qualification.
- `2239`: CPU control / storage / analysis plane — Git control, manifests, provenance, analysis, and management of the external `164` storage root.
- `164`: long-term large-data plane.
- old Docker `2233`: continues decouple-L1/L2 and other architecture work; remains a historical migration source until explicit closeout.

The V1 scientific/result files are historical observations and are not rewritten. In particular, `NEW_DESTINATION_RUNTIME_NON_EQUIVALENT_TO_R5` remains a correct observation of V1, but absence of GPU runtime in 2239 is no longer treated as an acceptance blocker for its corrected role.

Use the corrected branch `hrl/c16-ai-workload-2239-analysis-storage-v2b` for the next 2239-side phase. Do not execute any other instructions on this branch.