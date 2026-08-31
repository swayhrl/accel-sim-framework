# EP-L2 Motivation Figures — Final ChatGPT Review

Status: **DATA/SEMANTICS PASS; PACKAGING-ONLY CLOSEOUT REQUIRED BEFORE FINAL_PASS**

Reviewed formal provenance:

```text
Core      2a6a31591bc42023e5997cca969e4b672efe0405
Framework 02f36816f60afcff55e910cdef2b60937e691cdc
Branch    hrl/ep-l2-motivation-v0
```

## 1. Review result

The simulator/telemetry semantics, final 10-workload provenance, packet-identity WBUF lifecycle closure, fail-closed parser, exclusive blocker accounting, reuse-distance accounting and Stage-6 generated CSVs are accepted. No simulator rerun is required by this review.

The final pack does not yet satisfy the previously frozen Gate-Q packaging contract literally: the required `validation/` evidence directory is absent, and exact host wall/RSS numbers plus the concrete Release/direct-test/OFF-ON/git-status/git-diff-check command outputs are summarized but not independently exposed inside the final pack. Therefore do not self-label `MOTIVATION_FIGURES_FINAL_PASS` yet. This is a documentation/evidence-packaging fix only.

## 2. Scientific findings accepted from the current CSVs

### 2.1 Reuse structure

The measured stack-distance result does **not** support a strong "near-or-far bimodal" stack-distance claim. It supports a stronger short-locality claim:

- across all 10 workloads, the majority of reuse instances are very short;
- cumulative reuse distance <=32 ranges from about 68.8% (`cfd_097k`) to ~100% (`vectorAdd_4M`);
- cumulative reuse distance <=128 ranges from about 86.2% (`convolutionSeparable`) to ~100%;
- the >1024 distinct-block tail is effectively zero in this dataset.

Reuse-instance fractions are also high (~0.75 to ~0.999) and most workloads show very high epoch/slice-local unique-line reuse coverage. These numbers may support the statement that L2 demand locality is highly clustered/short-range in these workloads.

**Important claim boundary:** Figure 1 is an all-demand-reference reuse distribution. It does not by itself prove that a K-entry victim cache would recover misses, because many short-distance reuses may already be normal L2 hits. Do not turn the `<=K` bins directly into a victim-cache hit-rate claim. Exact C-entry FA-LRU capture is `distance < C`, as already documented.

### 2.2 Post-eviction reuse supplement

Real post-eviction rereference fractions vary materially:

- `cfd_097k` ~27.2%
- `FWT_7_21` ~24.8%
- `scan` ~15.2%
- `convolutionSeparable` ~3.7%
- `dwt2d` ~1.8%
- `btree` ~1.2%
- `vectorAdd_4M`, `spmv`, `sad`, `gemm`: zero/none in the measured epochs

This is valid evidence that some workloads do have real reuse after eviction, but the current supplement reports average reference-sequence/cycle distance rather than a post-eviction distinct-block stack-distance histogram. Therefore it is not yet evidence for a particular victim-buffer capacity K.

### 2.3 Structural blocking composition (WBUF=8 reference)

For workloads with nonzero projected blocked demand-miss admission cycles:

- `scan`: ~69.3% of eligible miss-admission cycles blocked; composition ~88.3% MissQ/lower, ~11.2% WB-path, ~0.3% Set/Assoc, negligible MSHR/Other.
- `vectorAdd_4M`: ~56.5% blocked; ~95.5% MissQ/lower, ~4.5% WB-path.
- `convolutionSeparable`: ~38.1% blocked; ~59.6% MissQ/lower, ~32.7% MSHR/meta, ~7.7% WB-path.
- `spmv`: ~44.4% blocked; ~93.2% MissQ/lower, ~6.8% MSHR/meta.
- `FWT_7_21`: ~55.3% blocked; ~75.2% MissQ/lower, ~24.8% WB-path.
- `cfd_097k`: only ~2.05% blocked overall, but all observed projected blockers are WB-path.
- `dwt2d`: ~7.59% blocked overall, all observed projected blockers are WB-path.
- `btree`: only ~0.14% blocked overall, all observed blockers are MSHR/meta.
- `sad` and `gemm`: zero projected blockers under this classifier.

This supports **resource heterogeneity** across workloads and strongly supports MissQ/lower-path pressure as the dominant admission blocker in several high-pressure workloads. It also identifies a real MSHR/meta component in `convolutionSeparable` and a WB-path component in `scan`, `FWT_7_21`, `cfd_097k`, and `dwt2d`.

It does **not** support a general Set/Associativity bottleneck claim: Set/Assoc is essentially absent except for a very small `scan` contribution.

### 2.4 WBUF shadow sensitivity

The C=4/8/16 views are accepted as trace-projected capacity pressure only, not performance results. WBUF lifecycle closure is valid on every formal broad row (`created == lower_accepted`, terminal active state zero). The data show meaningful capacity pressure especially in `scan`, `vectorAdd_4M`, `convolutionSeparable`, `FWT_7_21`, and `dwt2d`, with varying sensitivity to 4->8->16.

## 3. Figure-presentation recommendations (no simulator rerun)

The current two core figures are scientifically usable, but presentation should be tightened before slides/paper:

1. **Figure 1**: retain normalized reuse-distance stacks, but annotate or accompany each bar with `reuse_instance_fraction` (or an adjacent compact table). Otherwise viewers may read the bar as a fraction of all demand references rather than of reuse instances.

2. **Figure 2**: retain normalization over blocked cycles, but annotate each workload with its overall `blocked / eligible_miss_admission` rate. This is important because a 100% WB-path bar for `cfd_097k` (~2.05% total blocked) is very different from a 100%-ish dominant category in a workload with ~50-70% overall blocking. For zero-block workloads, label `No projected blocking` instead of leaving an unexplained empty bar.

3. **Figure 2S**: for cross-workload readability, consider a normalized sensitivity view (`would_block / WBUF opportunity` or `WB-path / projected blocked`) in addition to raw counts. Raw counts are valid but dominated by long workloads such as `scan`.

These are plotting-only refinements; keep the committed raw/aggregate CSVs immutable.

## 4. Required packaging-only closeout

Without rerunning any simulator workload, add to the final review pack:

```text
validation/
  BUILD_AND_TESTS.txt or equivalent
  OFF_ON_NEUTRALITY.csv/md
  HOST_OVERHEAD.csv/md
  GIT_CLEANLINESS.txt
  PACK_VALIDATION.txt
```

The evidence must expose, not merely state:

- exact Release build command/result;
- directed regression commands/results;
- parser/aggregation regression commands/results;
- vectorAdd/convolution/sad OFF-vs-ON cycles/instructions and existing parsed-output equality;
- host wall time and peak RSS values required by Gate L;
- `git status --short` and `git diff --check` results for the frozen source worktrees;
- SHA256SUMS verification result.

Update `SHA256SUMS`, README/VALIDATION_SUMMARY as needed. Do not alter the formal simulator source, frozen Core/Framework identities, raw broad rows, or scientific CSV values during this packaging closeout.

After this documentation-only amendment, request a delta review. If the evidence matches the already-reviewed state, the lane can be promoted to:

```text
MOTIVATION_FIGURES_FINAL_PASS
```
