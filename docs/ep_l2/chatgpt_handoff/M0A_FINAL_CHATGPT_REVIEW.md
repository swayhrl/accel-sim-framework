# EP-L2 M0a Final ChatGPT Review

Verdict: **M0A_FINAL_PASS**.

Reviewed final source/runtime anchors:

```text
Core candidate      666f0ba2d7b6a027f395346e274a934c19fdd3c1
Core parent         878f80869ce212e779df20b6421e4dc7f987825d
Framework runtime   2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d
Framework parent    aae62b66685f15437cecf0193934f628e6fac6ae
runtime config      d3aaf8a1a090c13e52985d60a70e7b3839aa0793d7db56722a7b3e8da3389b10
```

The final framework branch tip is packaging/analysis material; the simulator runtime source above remains the frozen candidate used by the accepted rows.

## Accepted evidence

- six required M0a-ON representative workloads are `COMPLETE_VALID`: `convolutionSeparable`, `scan`, `vectorAdd_4M`, `spmv`, `cfd_097k`, `sad`;
- required OFF/ON controls `vectorAdd_4M`, `convolutionSeparable`, and `sad` are exact in cycles and instructions;
- final strict analysis reports equality for deterministic B0/L1/DRAM parsed artifacts, terminal invariants, and the one-bit config-delta contract;
- Release build, M0a parser tests, final parser reprocessing, `git diff --check`, cardinality and terminal checks pass;
- no functional EP-L2 mechanism is enabled by M0a.

M0a therefore supplies valid Level-1/Level-2 observability for frontend structural blocked-cycle and useful-service accounting. It does not itself establish a functional mechanism benefit.

## Final workload-level observation

`m0_frontend_head_any_blocked_cycles / m0_frontend_head_observed_cycles` is accepted as the primary exact blocked-cycle fraction. The final six-workload data show strongly different regimes, including approximately:

```text
scan                  0.607
vectorAdd_4M          0.540
spmv                  0.417
convolutionSeparable  0.335
cfd_097k              0.0069
sad                   0
```

Temporal evidence is also valid for complete 5K/64-slice groups. In particular, scan has a sustained high-pressure profile rather than a single isolated spike.

## Required documentation-only semantic correction

The final `FIELD_SEMANTICS.md` wording is broader than the production source supports when it says reason fields are independently evaluated. The source preview contains early-return stages (for example WAD hazard / tag-all-reserved / WAD-full) and MSHR uses a prioritized `full_reason`; therefore a later reason can be unobserved because an earlier production stage stopped preview.

The accepted interpretation is:

```text
any_blocked_cycles:
  exact once-per-observed-cycle blocked total;

blocked_cycles_<reason>:
  production-visible / stage-primary reason accounting;
  reasons evaluated in the same reached stage may overlap;
  the vector is NOT an exhaustive simultaneous all-resource bitset;
  absence of a later reason does not prove that resource was available when preview stopped earlier.
```

This is a packaging/claim-semantics fix only. It does not require source modification or simulator rerun. Future M0a/M0b documentation and analysis must use this wording.

## Downstream promotion

With M1 already independently accepted, this review satisfies the final upstream dependency `M0A_FINAL_PASS` for the exact frozen M0a+M1 integration child. Exact matching descendants may be promoted without rerun according to the speculative execution policy.
