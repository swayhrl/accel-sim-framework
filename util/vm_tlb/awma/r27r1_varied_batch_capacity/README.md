# R27R1 varied-batch continuation tooling

- `gate_a_recheck.py` performs the bounded accepted-parent identity recheck and
  deliberately does not repeat the closed R27 207-item audit.
- `finalize_r27r1_negative.py` constructs the CPU-only Gate-B0 STOP evidence.
- `publish_r27r1.py` publishes and hash-closes compact raw/review evidence.

This continuation used the exact handoff and did not modify or resume closed
R27. The R26 CPU common checkpoint, R26 component/CCE source, model payloads,
and closed R27 review pack passed identity checks. The exact WikiText parquet
remained unavailable from the official current-main transport and existing
local sources, so tokenization, CUDA/JIT, GPU-lock acquisition, component
migration, capacity search, and trajectory work were not run.
