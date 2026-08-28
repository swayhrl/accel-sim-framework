# Corrected Conventional Sector-L2 Baseline v1 — provenance

This branch is intentionally a clean characterization baseline.  It contains
no Decoupled-L2, LateBind, AAD, token allocator, delayed allocation, or
experimental bank-model source.

## Source revisions

| Component | Repository | Branch | Revision | Role |
|---|---|---|---|---|
| Framework | `https://github.com/accel-sim/accel-sim-framework` | `hrl/l2-char-exp-v1` | `3016c658f810bdae9a14bf4534ee99e9945eedae` | Clean trace/simulation harness base. |
| Core | `https://github.com/accel-sim/gpgpu-sim_distribution` | `hrl/l2-char-baseline-v1` | `03c1fe443b1a46de695381662830bb4b9a4b3a00` | Corrected conventional sector-L2 source base. |
| Old framework reference | `git@github.com:swayhrl/accel-sim-framework.git` | `hrl/decoupled-l2-exp-v0` | `ae3b433c2bc7e8715c8dcc595efcd5df0654375c` | Read-only reference; not merged. |
| Old core reference | `git@github.com:swayhrl/gpgpu-sim.git` | `hrl/decoupled-l2-v0` | `971edd97e0c6b6e5bdc246a6838db0841cbaa2a2` | Read-only reference; not merged. |

The previous locally recorded framework revision
`6d6f8b20c89da0fcfaad5f3093fc4e186e76c39a` and core revision
`971edd97e0c6b6e5bdc246a6838db0841cbaa2a2` remain resolvable in the local
repositories.  No missing revision was reconstructed or guessed.

## Configuration identity

| Input | SHA-256 |
|---|---|
| `gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config` | `8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3` |
| `accel-sim/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config` | `19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e` |

The verified QV100 L2 configuration is:

```text
-gpgpu_cache:dl2 S:32:128:24,L:B:m:L:P,A:192:4,32:0,32
-gpgpu_cache:dl2_texture_only 0
-gpgpu_dram_partition_queues 64:64:64:64
-gpgpu_l2_rop_latency 160
-gpgpu_n_mem 32
-gpgpu_n_sub_partition_per_mchannel 2
```

This is a 64-subpartition, conventional eager-allocation sector-L2.  Its
replacement policy, IPOLY mapping, write-back policy, sector semantics, MSHR
sizes, and queue capacities are preserved unless a later focused commit says
otherwise.

## Environment observed at Phase A start

```text
g++ 11.4.0
CUDA 11.8
```

Build commands, exact wall-clock timestamps, exit status, and executable hashes
are recorded with the corresponding test result rather than inferred here.
