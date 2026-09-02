# Validation summary

## Build

Status: `PASS`

Verified command (return code 0; wall-clock 17 s):

```bash
CUDA_INSTALL_PATH=/usr/local/cuda-11.8 bash -c \
  'source /workspace/worktrees/gpgpu-sim-vm-core/setup_environment && \
   cd /workspace/worktrees/accel-sim-vm-core && \
   source ./gpu-simulator/setup_environment.sh && make -j8 -C ./gpu-simulator'
```

This uses Core SHA `73774727…` and Framework SHA `3016c658…`. The generated
binary is `gpu-simulator/bin/release/accel-sim.out`, SHA-256
`56ca98159450eb13c9374beaaeb01ab96c60337e674e2138102b1c2ecee25d51`.

## Trace smoke

Trace source: project `short-tests.sh` archive
`https://engineering.purdue.edu/tgrogers/accel-sim/traces/tesla-v100/latest/rodinia_2.0-ft.tgz`.
Archive SHA-256: `aeb7de478785856e4ac834d12be0e71ab0df297f43fc02650e2ca90dea66d8b1`.
Selected workload: `lud-rodinia-2.0-ft`, input `data_64_dat`, ten-kernel
`kernelslist.g` (SHA-256 `8b8cd7f1eeeedcdb48311fa33c949282904421d57f6342ca82fa1fe81716d952`).

| Run | Config files | Exit / wall-clock | Final cumulative cache/DRAM statistics |
| --- | --- | --- | --- |
| Project short-test smoke | `SM7_QV100/gpgpusim.config`, `SM7_QV100/trace.config` | `0` / 11 s | L1D 3828 accesses; L2 3828 accesses, 512 misses (13.38%); DRAM reads 512, writes 0 |
| Ampere smoke | `SM86_RTX3070/gpgpusim.config`, `SM86_RTX3070/trace.config` | `0` / 9 s | L1D 3828 accesses; L2 3828 accesses, 512 misses (13.38%); DRAM reads 512, writes 0 |

The per-kernel final record was: QV100 19,673 instructions / 20,923 cycles /
IPC 0.9403; RTX3070 19,673 instructions / 23,429 cycles / IPC 0.8397. Statistics
are emitted per kernel, while the cache and DRAM totals in the final record are
cumulative for the ten-kernel trace.

## Integrity checks

- `git diff --check` in both new worktrees: `PASS`.
- Worktree creation began from clean frozen source worktrees; the new Core tree
  remains source-clean. Framework changes are documentation only and listed in
  `CHANGED_FILES.md`.
- No command exceeded the 20-minute progress limit. The initial Framework setup
  attempt was stopped before it could clone a non-frozen Core; the subsequent
  build explicitly sourced the frozen Core setup first.
