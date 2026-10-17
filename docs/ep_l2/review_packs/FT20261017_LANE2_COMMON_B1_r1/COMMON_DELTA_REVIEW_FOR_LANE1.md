# COMMON_DELTA B1 — early reviewable handoff, r16

Authority92de53a63616f9fcc53f2058ad975c3c8f90b13c §2. Isolated Core branch `hrl/ep-l2-ft20261017-lane2-common-delta-r16-v1`, source **00edf6b9295fc3e4558654dec7ab6281dcb69d95** on producing common **088146f7f85b4073deb5d166a0a4484c7f3b48b2**. Semantic source change is commit3037ce12a9ea8a75a39f5fa18f32c047febcebba (three files); test-only commits precede/follow it. TVD r14 be5dcbe1 and its branch were not edited. No public Lane1 branch/build/output is modified.

## Confirmed defect and minimal fix

The real D512 line-key MSHR stores `m_has_atomic` for the entire line. `mark_ready` passes it to `baseline_cache::fill`, which previously marks every returned sector/byte mask dirty, even an ordinary sector and even after the atomic requester has retired. New `atomic_fill_masks` derives the intersection of the actual returned mask and live atomic requesters, using their real byte masks; D512 ready reporting and Tag dirty marking consume those masks. No new directory, requester pool, per-line field or class-layout change. Historical non-D512 behavior is retained.

A second actual FT defect was exposed independently: atomic MISS finishes with the old lower version label, unlike the existing atomic HIT completion marker. `ft_response_ready` now writes UID+1 only after its real bank grant on the pinned exact handle and before real response enqueue/commit. This is symbolic write-completion instrumentation; **the cache never calls do_atomic**. The actual callback remains in `memory_sub_partition::pop` (and existing shader paths). The controlled direct-cache fixture acts as consumer, invokes the real `mem_fetch::do_atomic` once per retired atomic UID and verifies no callback at fill. It is not proof of a numerical PTX atomic ALU or actual shader execution.

## Real old-red / new-green, same final fixture

Six actual l2_cache/MSHR/Tag tests each exit42 with a reason on unchanged official production archive implementation, and each exit0 after recompiling only gpu-cache.cc with the patch. Lower returns are deliberately reordered by the fixture; this is **not** extracted/reimplemented cache code. The old and new executables use the identical final fixture hash, exact official088146 unchanged archive hashes, matching C++17/11080 defines and enabled assertions. No full Accel-Sim rebuild. Compiler/link commands, logs, source/blob and binary identities are in the JSON receipts.

| Selector | Old observation | New observation |
|---|---|---|
| b1-read-first (U16) | ordinary sector1 alone becomes dirty mask2 | first mask0, final mask1, bytes4; symbolic label and later WB correct |
| b1-atomic-first (U16) | after early atomic retirement, ordinary return makes mask3/bytes36 | final mask1/bytes4; one atomic callback; later WB correct |
| b1-multi (native D512, FT off) | ordinary sector becomes dirty after atomic sector2 retires | two atomic sectors only mask5; bytes8; two callbacks, descriptor drain |
| b1-b16 | ordinary-first contamination | B16 copy/WB preserves corrected mask/bytes/label and drains |
| b1-dirty (U16) | pre-existing dirty sector3 + ordinary sector1 gives mask10 | first mask8, final mask9/bytes36; prior version retained in real WB |
| b1-version-only (U16) | atomic miss after one callback keeps old label100 | UID+1 label2; actual WB carries2 |

Final baseline/current executable SHA and fixture SHA are in `IDENTITY.json`. Initial pre-handoff fixture work/old-red logs are retained in the external result root; final evidence here compares dirty-sector WB obligations only, without inventing backing for unrequested sectors. All six current tests actually ran. No TVD test ran, and no 21-suite/full application/independent qualification claim follows.

## Merge entry and uncovered scope

Lane1 may review/pick semantic commit3037ce12 or apply `B1_MINIMAL_COMMON_SOURCE.patch` with --unidiff-zero to exact088146; apply the separate regression patch for tests. Do not merge the TVD branch or consume a new allocator. The current A1 patch may edit the same FT include; merge the response helper intentionally and keep A1's victim identity fix.

Not covered: numerical PTX ALU/CAS/reduction semantics, actual shader callback path, whole applications/traces, multi-slice atomics, concurrent same-sector atomics in FT (current pin guard serializes them), B8/U8 atomic runtime, multi-sector lower packets, shared RO/TVD/Ideal combinations, and independent Lane5 atomic qualification. Native multiatomic coverage does not claim concurrent FT atomics. Lane1 must rebuild its final integrated source and run affected gates before publishing a new producer, then Lane5 independently determines scope. No evidence here upgrades the old suspended R0/R1 or starts applications.

C1/C2 work remains active in this short Goal; this immutable B1 pack is published early so A1 need not wait. TVD rebase remains NOT_RUN and waits for the final official A1/common parent. Original TVD r14 three groups remain NOT_COMPILED_NOT_RUN.
