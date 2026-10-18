# Supplemental CPU evidence without compilation

Historical stage: this document records the earlier build-blocked snapshot. The later explicitly authorized CPU build and final9/9 qualification supersede its STOP/remaining-gap status; see LATEST_REPORT.md and FINAL_CPU_QUALIFICATION.json.

The continuation re-read Core `731be8548ad0fcc167ebfc49d5f1867f22034b4c`, Framework `6367c045e9d274f66ff949a8f8371e283dce81d6`, their read-back refs and clean worktrees. The original two build attempts are exhausted. No permission for another build has arrived. **ON acceptance remains STOP.** The two failed CTests are not relabelled PASS.

The existing library `4973fa934daa8dee09c72f8fe29aee123c6c98192205445147c3cb7363ee663e` exports the production `dtc_l1::oo_frontend(config)` constructor. Python ctypes called that symbol in isolated CPU children with the explicit verified x86-64 LP64 config ABI (56 bytes, finite/progressive/mode/ref_bits offsets0/1/4/52), aligned opaque object storage, and actual mapped-library path/SHA read-back. It did not inspect/edit internal C++ state. Supported cases returned. Unsupported cases produced exactly `DTC_PROGRESSIVE_WAKE_UNSUPPORTED_MODE_STOP` and SIGABRT, rather than accepting arbitrary crashes as success. The child restores default SIGABRT handling so a library crash reporter cannot substitute exit1; production assertions are intact.

| Existing production OO constructor | Result |
|---|---|
| ON, mode3/PAPER_OO, finite1 | PASS: returns |
| ON, all other combinations of modes0..4 and finite0/1 | PASS:9 exact diagnostic/SIGABRT rejections |
| OFF, modes0..4 and finite0/1 | PASS:10 constructor returns; new guard is inert |

The OFF cases mean this particular guard does nothing OFF. They do not claim every complete application configuration is globally supported: other existing mode/finite restrictions still apply. This is the actual OO constructor, not the full LDST constructor/parser routing for rejected configurations. Its scope is runtime guard behavior on the already-built production source; it does not validate the corrected C++ test binary.

The already-built `dtc_l1_normal_export_probe` was also run with the progressive option1 appended to an AD-owned config copy. It creates actual GPU/cluster/core/LDST objects and calls normal `gpu_print_stat(0)` three times per process, without a kernel, GPU cycle(), simulator execution thread or trace replay. Three processes cover no-event/1core, sparse-events/1core and sparse-events/8cores per cluster. Actual loaded ELF/library paths and hashes were verified. Debug-event limit remains0.

| Normal ON export | Result |
|---|---|
|9 normal statistics boundaries at cycles0/13/22 | PASS:64 unique SM summaries and LDST rows,33 histogram bins/SM, exact frame schema |
|Initial/no-event state | PASS: zero populations; all required rows present |
|Two one-waiter frontend API fills on SM0 | PASS: completed broadcasts2, fanout1 count2, first/last cycle sums6/6, span0; other SMs zero |
|Normal K1 ordinary pending/commit fixture with ON | PASS in this sparse API-prepared lifecycle; old print-state checks retained |
|LDST collectable/retired/common-boundary fields | Printed/parsed correctly at zero; **nonzero behavior remains UNPROVEN** because no cacheable LDST PIB instruction is injected by this existing fixture |
|Missing/duplicate SM, truncated frame, duplicate field, wrong histogram, wrong AD sentinel | PASS: all6 parser negative cases rejected |

The first supplemental parser run targeted the shared sentinel text in a preceding K1 frame instead of the AD frame. That negative-test mutation was narrowed to the AD header and every positive/negative check rerun successfully. No production code or assertion changed; the first raw attempt is retained. The supplemental parser intentionally rejects unexpected live LINE rows because these sparse fixtures reclaim their rows before the snapshots; it is not qualified here for arbitrary nonempty-pool input.

Original gaps remain: corrected C++ header fixture full completion, real LDST four-sector/duplicate/illegal/stale return tests, RF WB backpressure/ledger closure, partial admission, actual PROXY_FENCE sidecar with progressive consumers, common-time-boundary measurements, full newly added ON metrics population and exact C++ layout print. Header fanout/lifecycle subcases already passed as recorded previously; the real LDST fixture failure remains a failure. No payload/value, complete ISA, performance or full-simulation claim is made.

Reproducers: `scripts/run_existing_library_mode_guard.py`, `scripts/run_existing_normal_progressive.py`. Receipts: `EXISTING_LIBRARY_MODE_GUARD.json`, `EXISTING_NORMAL_ON_EXPORT.json`, `SUPPLEMENTAL_CPU_RECEIPT.json`. Raw outputs remain in AD-owned `/workspace/dtc-lane-ad-progressive-wakeup-174-v1/`. Compiler invocations added: **0**. Core SHA and build artifacts are unchanged.
