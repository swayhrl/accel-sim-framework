# COMMON_DELTA_REVIEW_FOR_LANE1 — r16 closeout

Authority: `92de53a63616f9fcc53f2058ad975c3c8f90b13c` §2. Producing public parent is **088146f7f85b4073deb5d166a0a4484c7f3b48b2**, not the older c948 screenshot. Official R0.1 producer21/21 does not imply independent scientific acceptance or close A1/B1. Isolated execution branch **hrl/ep-l2-ft20261017-lane2-common-delta-r16-v1**, final source **099aeb5ac002ddc03ab8dc295caa1333d9aa50e1**. Original Lane2 TVD branch remains at **be5dcbe1fa5b9a501e81a77a6c399e6f6530e536** with no edits/rebase/tests. Lane1's public branch/build is untouched.

## B1: confirmed production correctness defects, source fix and actual evidence

The early immutable `FT20261017_LANE2_COMMON_B1_r1` was published at Framework292d92749 to allow Lane1 to consume B1 before C1/C2 closeout. Minimal semantic commit **3037ce12a9ea8a75a39f5fa18f32c047febcebba** changes three files. Test-only commits are separate; no TVD source is needed.

`mshr_table::m_has_atomic` is line-wide and stays true after an atomic requester retires. In descriptor/line-key mode, `mark_ready` used that bit for every sector return; `baseline_cache::fill` then dirtied the returned packet's sector and byte mask. The fix derives `atomic_fill_masks` from actual **live** atomic requesters intersecting the actual returned sector mask, and uses their byte masks. No new per-line field, pool, class data-layout change or data array is introduced. Non-D512 historical behavior is explicitly unchanged.

The independent atomic-MISS case also exposed a stale FT symbolic version after completion. On a successful response-bank grant for the pinned exact handle, `ft_response_ready` now applies UID+1 to the atomic's sectors before response enqueue/commit, consistent with the existing symbolic atomic-HIT convention. This updates an instrumentation label, **not numerical atomic bytes**. Cache code does not invoke the ALU callback. The actual callback responsibility remains `memory_sub_partition::pop` / the existing shader path; the controlled direct-cache consumer calls the real `mem_fetch::do_atomic` exactly once per retired UID and verifies no callback at fill. No real PTX ALU or shader execution is claimed.

Seven B1 cases have actual old-red/new-green evidence:

| Case | Actual old result | Actual corrected result |
|---|---|---|
| U16 ordinary sector1 before atomic sector0 | first dirty mask2 | first0, final1/4 bytes; WB and label correct |
| U16 atomic first, retire it before ordinary return | late fill mask3/36 bytes | final1/4 bytes, callback once, correct WB |
| Multiple native D512 atomics (FT off), out-of-order retirement | ordinary late sector dirtied | exactly atomic sectors0+2, mask5/8 bytes, callbacks2, descriptor drain |
| B16 ordinary-first/copy/WB | ordinary sector dirtied | correct4 dirty bytes and version through actual copy/WB |
| Pre-existing dirty sector3 + atomic0 + read1 | first mask10 | first8, final9/36 bytes, prior sector3 version preserved |
| Atomic-MISS completion alone | old label100 after one callback | label2=UID+1, actual WB carries2 |
| Downstream WB counterexample (do not abort on intermediate Tag defect) | **real WB mask3 /36 dirty bytes /old atomic label100** | **real WB mask1 /4 dirty bytes /atomic label2** |

The first six cases use the identical final fixture on old official archive code and new gpu-cache TU (`00edf6b9` fixture freeze). The seventh uses the identical later fixture on old official code and final corrected source099aeb5a. It deliberately reaches real eviction before rejecting the old packet. Failures exit42 with the specific reason, not arbitrary nonzero exits. Lower-return order is controlled by the fixture, while MSHR, Tag, cache fill, Payload, bank retry and WB producers are the actual compiled implementation. No extracted cache algorithm substitutes for them.

## C1: actual reachability and observer-only correction

A real U16/64-set/16-way cache is host-prefilled with1024 Tag owners, a dirty replacement is attempted while its actual bank is busy, and the producer retains the old resident plus its reserved landing. Observed **resident role1025 / Tag-visible1024 / pending landing1 / physical slots1168 / physical free143**. This is reachable, not merely a `1024-1025` arithmetic toy.

The old `resident_free()` returns4294967295. The actual subpartition M0 sampler, observing two such cycles, prints **resident_free_sum8589934590**, despite keeping occupied_max1025. Corrected shared `nominal_resident_headroom` saturates the legacy nominal role headroom at0; actual new M0 free_sum is0. Occupied sum/max still count the original allocation **role** and are not relabeled as Tag occupancy. The output explicitly states:

- `resident_legacy_occupied_scope=PAYLOAD_ROLE`
- `resident_legacy_free_scope=SATURATED_NOMINAL_ROLE_HEADROOM`
- `resident_legacy_over_nominal=1` on this cumulative sample; window streams mark it UNAVAILABLE because old window max/min were not collected.

New `EPL2RESIDENTOBSV1` separately reports Tag capacity/visible, pending landing, resident role/other-unbound, and physical capacity/occupied/free. It is explicitly **instant_at_m0_print**, not an average of the preceding window. In the real pending state it prints1024/1/1025 and1168/1025/143. No Tag/Payload capacity, allocator, arbitration or admission policy changes. Old overflowing values remain invalid for paper causal graphs; new instantaneous counts cannot be presented as window distributions. This conservative observer fix adds no accumulator fields or common object-layout changes.

## C2: actual bypass-only backpressure

Both L2-off and texture-only/global branches previously push a third request into the actual two-entry L2_dram FIFO and abort in `fifo_pipeline::push`. The minimal fix guards **only the actual bypass else-branch**. While full, no status change, requester admission, enqueue or frontend pop occurs; the same head waits until credit returns. The corrected real subpartition tests fill the FIFO, hold the third head for four cycles, restore lower credit, and verify three exact-once responses plus queue/tracker closure.

FT texture bypass additionally needs the requester token already fixed in the separate TVD r14 branch: common088146 lacks it, so COMMON_DELTA records admission at the successful bypass enqueue before the existing return audit. Keep this insertion **once** when later rebasing TVD. The L2-off token helper remains its existing no-op. A separate actual cache-hit control passed both before and after: a warm normal cache hit replies while lower FIFO occupancy stays2. No global lower-full gate is added to hits, merges or locally absorbed writes.

One first new L2-off fixture run segfaulted after the three replies because the fixture called a cache-specific leak helper with no cache instance. GDB identifies the call. The fixture now checks the actual disabled-mode queues/tracker/busy state, retaining the enabled FT leak check for texture bypass. This is a fixture correction, not a passing L2-off cache-statistics claim. Initial failure/GDB/final success are all retained.

## Exact validation scope and resource accounting

`VALIDATION_MATRIX.json` binds each of **12 distinct cases** to its actual tested source, executable hash, logs and status. There are11 meaningful old-red cases and one old-green normal-hit control. Green evidence is at pinned component revisions, **not a claim that all12 ran on one final executable**: six early B1 cases at00edf6b9; C1 transient/C2 texture+hit atd8e323cf; real M0 output and corrected L2-off fixture ata4447cc6; downstream WB at final099aeb5a. Source099aeb5a is compiled and its downstream B1 WB test actually passes. No already-green unrelated suite is replayed; historical producer21, TVD three new groups and listener/getter/static suites were not run.

Only the new fixture TU and changed `gpu-cache.cc` / `l2cache.cc` TUs were compiled, then linked against content-hashed unchanged official088146 archives. The class-data layouts are unchanged; this intentionally limited object reuse is **not a fresh full producer rebuild** and does not qualify other paths using cached inline code. Lane1 must cleanly rebuild all affected header dependencies in its integrated release. Commands/compiler/assertion flags, source hashes, archive hashes, executable hashes and actual `/usr/bin/time` build logs are frozen. Compact final outputs strip debug sections only; assertions remain enabled, all unstripped earlier artifacts are retained.

Central leases **bc33e109a0f54d4c9e9ffc5b930737e4** (early B1) and **7ac918a37628491a86b883da4c3c54cf** (C1/C2/final downstream gate) each reserved1 CPU/4GiB after current resource checks. Both are RELEASED. Retained build allocation462848000B stays below the declared512MiB output budget. Actual workspace safety floor remained above50GiB; no lowered policy, parallel compiler, full Accel-Sim build, formal app, waiter, cleanup or migration. A C1/C2 driver's initial metadata accidentally quoted the prior B1 lease; the initial bytes and an explicit attribution correction are retained, alongside the actual C1/C2 admission-before-build and release receipts. No unleased compile occurred.

## Lane1 merge and required remaining gates

Use `COMMON_DELTA_SOURCE_ON_088146.patch` with --unidiff-zero on the exact parent, or inspect B1 semantic3037ce12 and C1/C2 semanticd8e323cf plus formatter refinement ata4447cc6. The source patch touches only four common production files; the regression patch is separate. Do not merge the TVD branch, overwrite the frozen R0.1 binary/21 logs, or treat this as an A1 repair. Preserve Lane1's actual pending-victim transaction fix when resolving any overlap in the FT include/Tag code.

For the next exact integrated producer, run the finite12 selectors in `NEXT_INTEGRATED_GATES.json` once after a real central admission and clean affected build. Lane1's A1 16-way and existing producer gates remain its responsibility; B1 must not make A1 wait indefinitely. Lane5 remains the independent scope/qualification authority. No application launch or old acceptance restoration follows from this delivery.

Uncovered atomic scope: numerical PTX atomic/CAS/reduction semantics and returned values; actual shader/partition dequeue callback execution (the direct fixture models that consumer with the real callback); concurrent same-sector atomics under FT's pin serialization; multi-lane/warp interactions; multi-sector lower return packets; B8/U8 atomic runtime; multi-slice/whole traces; RO/TVD/Ideal combinations; independent Lane5 atomic science. No workload is assumed atomic-free from its name. Broader acceptance requires its own evidence; no ports, buffers or oracle scope were changed.

TVD follow-up is **TVD_R2_REBASE_NOT_RUN**. The exact entry/conflict list is in `TVD_R2_REBASE_NOT_RUN.md`; r14's clean cost, texture eligibility and all old packs remain unchanged. There is no continued resident work after this bounded closeout.
