# EP-L2 M0a Interim ChatGPT Review

Date: 2026-08-30

Review status: **CONDITIONAL PASS FOR SPECULATIVE INTEGRATION**.

This is not `M0A_FINAL_PASS`. The live `scan` validation remains a final promotion gate.

## Frozen source candidate

```text
Parent Core       878f80869ce212e779df20b6421e4dc7f987825d
M0a Core          666f0ba2d7b6a027f395346e274a934c19fdd3c1
Parent Framework  aae62b66685f15437cecf0193934f628e6fac6ae
M0a Framework     2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d
runtime config    d3aaf8a1a090c13e52985d60a70e7b3839aa0793d7db56722a7b3e8da3389b10
```

The Core is exactly one commit over the accepted D512 parent and changes only M0a configuration/telemetry producer state in `gpu-cache.h`, `gpu-sim.cc`, `l2cache.h`, and `l2cache.cc`. Framework changes are M0a config/runner/parser/analyzer/tests. No payload allocator, MSHR/descriptor semantics, bank arbitration, lower routing, scheduler, or DRAM functional policy is changed by the M0a feature switch.

## Existing timing-neutrality evidence

Required OFF/ON controls completed so far:

```text
vectorAdd_4M       73,873 == 73,873 cycles
convolution        292,211 == 292,211 cycles
sad                 110,653 == 110,653 cycles
```

Instructions also match exactly for all three. Five M0a-ON representative rows are locally complete: vectorAdd, convolution, spmv, cfd, sad. `scan` remains live and must not be disturbed.

This is sufficient to treat the implementation source as frozen for speculative integration, but final M0a acceptance still requires strict old-field B0/L1/DRAM/terminal equivalence and final scan parsing.

## Important semantics correction required before final M0a closeout

The current producer obtains reasons from the production `preview_access()` path. That path intentionally short-circuits on some early blockers (for example WAD same-address hazard, tag-set all-reserved, and WAD-full), and the MSHR interface exposes one prioritized `full_reason` among per-address/Line-MSHR/descriptor conditions.

Therefore the per-reason M0a fields are **not an exhaustive independent all-resource bitset**.

Final field documentation/analyzer wording must use the narrower accepted semantics:

```text
m0_frontend_head_any_blocked_cycles
    exact once-per-observed-cycle blocked total;

per-reason blocked-cycle fields
    production-visible / stage-primary reason accounting from the exact
    preview path; some simultaneously evaluated predicates may overlap, but
    earlier short-circuit stages and prioritized MSHR full_reason prevent an
    exhaustive multi-cause interpretation.
```

Do not sum reason counters and do not claim that an absent later reason proves that resource was available in a cycle stopped by an earlier preview stage.

This correction can be documentation/parser/analyzer semantics only; do not change the live source candidate or invalidate the running scan merely to manufacture a full independent bitset. A future M0b field family may add a side-effect-free exhaustive bitset if scientifically needed.

## Final M0a items still required

Before `M0A_FINAL_PASS`:

1. live scan completes normally with the frozen source/config;
2. strict OFF/ON comparison checks deterministic existing B0/L1/DRAM artifacts and terminal invariants, not only cycles/instructions;
3. final pack documents the narrowed reason semantics above;
4. add/retain directed validation for once-per-cycle accounting, held-head behavior, useful-admit/useful-response boundaries, and parser fail-closed behavior;
5. final review pack and hashes are complete.

## Decision

The exact frozen M0a source candidate is **approved as an input to a speculative M0a+M1 integration child**.

Integration evidence remains `SPECULATIVE_PENDING_GATE` on `M0A_FINAL_PASS` and `M1_FINAL_PASS` and may not be promoted if the final M0a scan/equivalence gate exposes a source/timing defect.
