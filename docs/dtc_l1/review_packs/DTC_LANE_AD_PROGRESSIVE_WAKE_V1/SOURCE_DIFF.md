# AD source difference / allowlist

Parent Core: `e32afdcf44be3374ff36d22568ed01a075459b6f` (fixed X2, independently fetched/read back). Framework review parent: `631eb6418f6e7f1f548afd33351cbc0d98d27145`. Authoritative final IDs and artifact hashes are in publication/identity receipts. Source trees are isolated AD worktrees on huangrulin-174, uid0.

Allowed changes only:

- `src/gpgpu-sim/dtc-l1-common.h`: default-false config field, shared fail-closed guard, AD data/notification separation and bounded observer, consumed-prefix compaction, AD state assertions, separate common-boundary timestamp. Other frontend constructors reject direct ON API misuse; their routing/service bodies remain unchanged.
- `src/gpgpu-sim/gpu-sim.cc`: register exactly `-gpgpu_dtc_l1_progressive_wakeup`, default0.
- `src/gpgpu-sim/shader.h`: config field, observer delegation declarations, two LDST counters.
- `src/gpgpu-sim/shader.cc`: constructor guards and OO-only config transfer; common-boundary/ready observation and retired sum; normal-statistics delegation guarded ON.
- `CMakeLists.txt`, three new CPU test sources: directed header/LDST tests and fixed-X2 differential targets. The baseline header is read from the pinned Git object into the AD build directory, never written into another source tree.

No edits to response acceptance, lower candidate/create/inject routing, memory-cycle admission, LDST ready selection, LDST WB-retire/ledger closure, source invalidate, ordinary flush or K1 observer logic. `SOURCE_ALLOWLIST.json` verifies unchanged critical function bodies and exact changed paths. Full review delta is `SOURCE_DIFF.patch`.

Unchanged simulated capacities and ports: 128B logical line / four legal 32B responses; configured physical pool and PIB; four tag banks, one per bank/four total; allocation width4; metadata notifications4 per SM/cycle; collection4 sectors/cycle; lower create/inject limits and one retire/cycle; original complete->metadata +1, ready->collect +1, collect-done->WB +1. No performance run or bandwidth increase was performed. AD changes which notified consumer can reach the unchanged collection/eligible gate.

OFF preserves old state transitions, public counter meanings and output lines. New host fields, guards and type layout exist even OFF; this is source/ABI growth, not a claim of byte-identical objects or host instruction execution. Deterministic header traces across ordinary paper Base/IO/OO and modern, plus real normal-print boundaries with K1 off/on, were compared against fixed X2. This is targeted equivalence evidence, not exhaustive workload equivalence. See OFF_DIFFERENTIAL.json.

Resource cost: bounded added bookkeeping, host vector prefix moves (only ON), an ON per-service-edge observer over live entries, and ON shadow waiter assertions. These CPU operations do not consume modeled GPU cycles/ports; their host cost is not a measured hardware/performance result. Exact/derived host layout costs are recorded with the test results. No new payload storage, coherence protocol, refill source, L1 MSHR, simulator campaign or workload-specific branch was added.
