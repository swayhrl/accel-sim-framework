# Codex Goal — Lane F / node109
## AWMA R20R3P1 profiler admission repair and automatic R20R3 resume V1

Date: 2026-10-01

Repository:
`swayhrl/accel-sim-framework`

Execution branch:
`hrl/awma-r20r3p1-profiler-repair-resume-109-v1`

Scientific parent:
`fa292a11dbc196b65ebe1f3a67f39a7837046995`

Stage:
`AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1`

This is one continuous solve-and-continue Goal.

The order is fixed:

1. qualify the installed Nsight Systems toolchain with a tiny engineering canary;
2. if canary passes, run exactly one repaired scientific B0 profile on the same four discovery entries;
3. if the scientific profile produces attributable stage timing, resume the original R20R3 stage-selection rule without modification;
4. if one stage is selected, implement exactly one R20R3 active-world diagnostic and run the original correctness/discovery/conditional-holdout sequence;
5. STOP at the first scientific or engineering stop condition.

Do not ask for another confirmation between these stages.

---

# 0. Frozen scientific authority

Reuse exactly:

- MuJoCo Warp source:
  `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`
- solver.py blob:
  `090061796792f4d11408eaa69b4ef3c44465c705`
- RTX4080 / SM89
- B=1024
- G1 hfield / shuffle_dance / Menagerie authority inherited from R20/R20R1
- sparse Newton / pyramidal / conditional graph
- iterations=10
- ls_iterations=20
- original solver tolerance / ls_tolerance
- revised R20R2-reviewed numerical contract
- exact four discovery solver entries:
  - t128 `8f3d7015979e959625f3b1d1cd1efb3fb2dea65b4e07bc9c9f1795b30dccd85d`
  - t136 `07c012c0d17eaba3522bcc35016eff581612c138b7c876dff64455788344e883`
  - t144 `4177e0a8a509608651f85f055877576cd71d3f25a40ab2451f276c9b08cdfda6`
  - t152 `42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87`
- original R20R3 source-eligible stage audit and frozen ranking rule.

Read before execution:
- parent `PROFILE_FAILURE_AUDIT.md`
- parent `ELIGIBLE_STAGE_AUDIT.md`
- parent `REVISED_NUMERICAL_CONTRACT.md`
- parent `RUN_RECEIPTS.json`
- handoff review:
  `docs/vm_tlb/chatgpt_handoff/awma/r20r3_active_world_solver_native_v1/STATUS_AFTER_R20R3_PROFILE_STOP.md`

Do not edit historical parent evidence.

---

# 1. G0 — Nsight Systems installation receipt

CPU-only first.

Record:
- exact `nsys --version`
- `which nsys`
- `nsys status --environment` or the closest supported environment-status command for this installed version
- help text for:
  - `profile --capture-range`
  - `--nvtx-capture`
  - `--output/-o`
  - overwrite option
  - export behavior
- exact support for `nsys export --type sqlite`
- exact support for `nsys stats`

Write:
`NSYS_TOOLCHAIN_RECEIPT.md`

Do not assume the CLI matches current online docs if installed version differs.

The likely parent issue is a capture trigger mismatch:
- parent Python uses `nvtxRangePushA` dynamic strings;
- the parent command used `--capture-range=nvtx --nvtx-capture=R20R3_PROFILE`;
- current Nsight docs note registered-string-only behavior by default in this mode.

Verify installed-version semantics from local help where possible.

---

# 2. G1 — tiny profiler admission canary

This canary is engineering only.

Use a tiny isolated Python/Warp or CUDA workload with:
- one known GPU kernel
- one outer NVTX range emitted by the same direct `nvtxRangePushA` / `nvtxRangePop` mechanism used by R20R3
- no scientific solver input.

Run under the GPU lock.

Use:
- an explicit absolute output prefix under the new R20R3P1 campaign root
- overwrite enabled
- `--trace=cuda,nvtx`
- `--capture-range=nvtx`
- exact canary `--nvtx-capture=<name>`
- `NSYS_NVTX_PROFILER_REGISTER_ONLY=0` if supported/needed by this installed version
- `--sample=none`
- `--cpuctxsw=none`

Prefer:
1. generate a nonempty `.nsys-rep`;
2. then export SQLite explicitly with `nsys export --type sqlite` rather than relying on implicit export, unless installed help proves a direct path is reliable.

Canary passes only if:
- nsys exit code 0
- expected `.nsys-rep` exists and is nonempty
- SQLite export exists and is nonempty
- a simple stats or SQLite query proves:
  - the NVTX range exists
  - at least one CUDA kernel row exists inside/associated with the capture.

Record:
`NSYS_CANARY_RECEIPT.json`

No scientific stage timing may be read or inferred from this canary.

At most two bounded engineering repairs are allowed for the canary, limited to:
- installed-version CLI syntax
- registered/unregistered NVTX capture setting
- output/export path handling.

Do not change driver, CUDA, application source, solver source, or install a new profiler version.

If canary cannot qualify:
`R20R3P1_PROFILER_NOT_QUALIFIED`
STOP.

---

# 3. G2 — repaired scientific B0 profile

Only after canary passes.

Reuse the exact parent R20R3 OFF/B0 scientific workload:
- same source overlay OFF
- same four snapshots
- same order 128 -> 136 -> 144 -> 152
- same parent numerical validator
- same nested NVTX ranges
- same solver graph.

Do not regenerate scientific inputs.

The one repaired scientific profile is the only scientific NSYS collection authorized in R20R3P1.

Use:
- explicit absolute output prefix
- validated NVTX capture setting from canary
- report generation first
- explicit SQLite export second
- validated stats/query path from canary.

Scientific profile qualifies only if:
1. all four solver replays pass the revised numerical contract;
2. nonempty `.nsys-rep` exists;
3. nonempty SQLite exists;
4. CUDA graph child-kernel rows are present;
5. kernel/event-scope attribution is sufficient to compute cumulative GPU kernel time for every source-eligible stage in the already-frozen `ELIGIBLE_STAGE_AUDIT.md`;
6. nested per-entry identity is recoverable so cumulative time is across exactly t128/t136/t144/t152.

If report exists but eligible-stage attribution is ambiguous:
`R20R3P1_PROFILER_NOT_QUALIFIED`
STOP.

No second scientific NSYS retry.

Write:
- `REPAIRED_PROFILE_RECEIPT.json`
- `REPAIRED_B0_PROFILE_SUMMARY.tsv`

---

# 4. G3 — resume original R20R3 stage selection exactly

Do not rewrite `ELIGIBLE_STAGE_AUDIT.md`.

Eligible candidates remain only those already source-qualified in parent.

Use the original ranking rule:
- cumulative B0 GPU kernel time over t128,t136,t144,t152
- choose largest eligible stage
- tie within 5% -> fewer distinct source functions/kernels to modify.

No expected-speedup judgment.

Freeze:
`SELECTED_STAGE.md`

If the selected stage is the source-eligible incremental gradient stage but cannot be implemented as one bounded diagnostic while preserving within-world math, STOP:
`R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`

Do not fall back to the second-ranked stage.

---

# 5. G4 — exactly one active-world diagnostic

Resume the parent R20R3 candidate rules unchanged.

Candidate must:
- be opt-in/default OFF
- build active IDs from current online `ctx.done`
- use no future niter
- preserve logical world identity
- preserve within-world EFC/J order
- preserve block/tile/reduction math
- preserve solver stop predicates
- include list/queue/reset/index/sync costs
- actually reduce inactive-world execution footprint.

Only one worker configuration.

No timing sweep.

Derive worker configuration from device/kernel occupancy or one deterministic device rule before formal timing.

At most two bounded correctness/liveness engineering repairs.
No second candidate.

Write:
`DIAGNOSTIC_CONTRACT.md`
before formal candidate timing.

---

# 6. G5 — candidate correctness

Use all four discovery entries.

Apply the frozen R20R3 numerical contract:
- exact entry/options
- exact constraint/world identity
- exact nefc
- exact outer solver_niter
- no new capacity overflow
- finite outputs
- ctx.done
- frozen qacc/qfrc_constraint/efc.Ma/valid-efc.force screens
- qfrc source relation
- no stale/hidden-state evidence
- LS_ITERATIONS recorded but not a hard equality gate by itself.

Any material LS path propagation remains failure.

If any entry fails:
`R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED`
STOP.

---

# 7. G6 — formal discovery complete-solver timing

Only after correctness passes.

No profiler during formal timing.

For each t128/t136/t144/t152:
- B0 = candidate OFF
- S1 = candidate ON
- 3 paired groups
- 2 warmups/arm/group
- 5 formal samples/arm/group
- alternate arm order by group
- exact same frozen solver entry restored for each sample.

Primary boundary:
`frozen solver input ready -> complete solver.solve outputs committed`

S1 includes all active-list / worker / synchronization costs.

Record all wall/event samples.

Discovery MATERIAL gate remains exactly:
1. all four correctness pass
2. all three aggregate groups favor S1
3. median aggregate complete-solver improvement >=5%
4. gap >3x larger-arm aggregate MAD estimate
5. no less solver work / changed niter / changed coverage.

If stable below threshold:
`R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`
STOP.

If mixed:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`
STOP.

No second candidate or worker count.

---

# 8. G7 — automatic holdout only for discovery survivor

If discovery MATERIAL, continue automatically without asking.

Generate/freeze holdout solver entries:
384, 392, 400, 408

using original B0 source and original control generation only.

Freeze all four before candidate timing.

Apply the same correctness and formal timing protocol.

No tuning.

Success:
`R20R3_ACTIVE_WORLD_SOLVER_RESPONSE_REPRODUCED`

Requires:
- all four holdout B0 inputs qualify
- all S1 numerical gates pass
- all three holdout aggregate groups favor S1
- median aggregate improvement >=5%.

Otherwise:
`R20R3_RESULT_MIXED_NEEDS_REVIEW`

Even success does not authorize 174 or hardware.

---

# 9. Resource and scope limits

Across R20R3P1:
- profiler engineering canary: allowed, not scientific
- scientific NSYS: exactly 1 repaired B0 profile
- NCU: 0
- NVBit: 0
- SASS: 0
- Accel-Sim: 0
- node174 compute: 0

All CUDA/JIT/capture/replay/profiling:
`/data/c16/locks/c16_gpu_campaign.lock`

Large raw -> node164.
109 active replicas only.

Do not:
- change scene/batch/replay
- train policy
- change solver iterations/ls_iterations/tolerance
- alter collision/contact/EFC construction
- change precision
- sweep worker counts
- change stage ranking
- run whole 32-step B0/S1 trajectory timing
- claim whole physics-step or RL speedup
- design hardware
- start 174.

Ordinary engineering issues solve-and-continue.
Scientific contract/identity change -> STOP.

---

# 10. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1/`

At minimum:
- README.md
- FINAL_DECISION.md
- PARENT_AUTHORITY.json
- NSYS_TOOLCHAIN_RECEIPT.md
- NSYS_CANARY_RECEIPT.json
- REPAIRED_PROFILE_RECEIPT.json if reached
- REPAIRED_B0_PROFILE_SUMMARY.tsv if reached
- SELECTED_STAGE.md if reached
- DIAGNOSTIC_CONTRACT.md if reached
- CANDIDATE_SOURCE_DIFF.patch if reached
- CANDIDATE_CORRECTNESS.tsv if reached
- DISCOVERY_TIMING.tsv if reached
- DISCOVERY_DECISION.md if reached
- HOLDOUT_INPUT_RECEIPTS.tsv if reached
- HOLDOUT_TIMING.tsv if reached
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

NOT_RUN is explicit for unreached stages.

---

# 11. Closure

Publish one exact commit.
Push/fetch-back verify commit/tree.
Release GPU lock.
Terminate campaign GPU processes.
Clean worktree.
STOP.

Final Chinese report must state:
- whether profiler admission was repaired
- whether stage ranking became available
- selected stage if any
- what candidate changed
- discovery complete-solver response
- holdout result if triggered
- what evidence supports and what remains unknown.

Do not present this as a whole-physics-step or hardware result.
