# R18 preparation | Engram serving lookup

Date: 2026-09-30

Final state: `R18_ENGRAM_DIRECT_SOFTWARE_COVERAGE_CLOSES_QUESTION`

This card is closed at the source/nearest-neighbor gate. It is **not** a Native negative.

The detailed preparation record is:
`../rounds/2026-09-30_ROUND_18_ENGRAM_SERVING_SCREEN.md`

The source closeout is:
`../rounds/2026-09-30_ROUND_18_ENGRAM_CLOSEOUT.md`

## Why closed

The original surviving question was whether real host-resident Engram serving retained a material lookup-path residual after mature overlap/page controls.

Fresh review of current vLLM/SGLang and merged real-model Engram performance work showed direct mature coverage of:
- pinned-host/UVA lookup;
- asynchronous prefetch before Engram-layer consumption;
- persistent staging buffers and per-layer completion events;
- serialized background lookup to avoid SM interference;
- transparent-huge-page backing specifically addressing GPU-MMU/TLB pressure;
- shared host-table / DP organization;
- TP sharding of the large Engram `wkv` projection;
- explicit hot-row cache/rows-only overlap as an upstream nearest-neighbor direction.

Because the core causal space is already directly implemented and quantitatively evaluated on real DeepSeek-V4.1, further isolated node109 lookup work would be characterization rather than a new AWMA problem.

## Reopen condition

Reopen only if a different real workload provides evidence of a residual **after** these strong software baselines. Do not reopen by substituting a reduced/synthetic table or by searching for a positive Ada microbenchmark.

No execution result or hardware claim is made here.
