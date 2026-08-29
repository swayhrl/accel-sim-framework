# EP-L2 Final 26-Run Target-Baseline Handoff

This stage is automatically authorized **only after** `C7E_ACCEPTANCE_CRITERIA.md` is fully PASS and the C7e closeout states exactly:

```text
READY_FOR_FINAL_26_RUN
```

No human pause is required between C7e and this campaign if that gate is satisfied.

## Objective

Run the one intended full Target-Baseline campaign:

```text
13 frozen workloads
x
{B0-Legacy, B0-Banked}
@
850 MHz
=
26 formal runs
```

Then generate an analysis-ready package and a conservative first-pass bottleneck report. Stop before 1 GHz, RO/TVD/Unified opportunity instrumentation, or functional EP-L2 mechanisms.

## 1. Freeze the exact formal source pair

Immediately after C7e acceptance, record:

```text
FINAL_CORE_SHA
FINAL_FRAMEWORK_SHA
```

and freeze them for the entire campaign.

The runner must use its fail-fast expected-SHA/clean-worktree/config-hash gate for every launch.

Do not modify runtime Core/Framework source after the formal campaign begins.

## 2. Fresh formal result root

Use only:

```text
docs/ep_l2/target_baseline_results_final_850/
```

or another newly created path explicitly declared in the campaign manifest.

Never mix in:

```text
C5c results
C6d smoke/prefill
C7d diagnostic samples
pre-fix Banked results
```

These remain diagnostic/obsolete evidence.

## 3. Frozen workload roster

Use exactly the reviewed 13-workload roster already encoded in the runner:

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
cfd_097k
dwt2d
sad
sgemm
btree
3mm
gemm
FWT_7_21
FWT_11_19
```

Do not change inputs, trace paths, problem sizes, configs, or aliases during the campaign.

## 4. Frozen variants

Run exactly:

```text
B0-Legacy @850 MHz
B0-Banked @850 MHz
```

with the frozen target configuration.

No Unified, RO, TVD, graphics borrowing, 1 GHz, or sensitivity variants belong in this campaign.

## 5. Formal preflight

Before launching all 26, run a short promotable preflight using the final runner and final result root:

```text
spmv B0-Legacy
spmv B0-Banked
cfd_097k B0-Legacy
cfd_097k B0-Banked
```

These four runs count toward the 26 if all are `COMPLETE_VALID` and their manifests match the exact final source/config pair.

Preflight must prove:

```text
expected-SHA gate active
formal config hashes correct
parser outputs present
all mandatory target schemas present
terminal invariants PASS
no C6d artificial bank staging
```

If preflight fails due a systemic source/telemetry correctness problem, enter the repair rules in `CODEX_TARGET_GOAL.md`; do not launch the remaining 22.

## 6. Campaign scheduling for wall-time efficiency

After 4/4 preflight PASS, launch the remaining formal runs using safe host-aware concurrency.

Prioritize long workloads early so they overlap with shorter runs:

```text
scan Legacy/Banked
3mm Legacy/Banked
sgemm Legacy/Banked
convolutionSeparable Legacy/Banked
```

Then fill available slots with the remaining workloads.

Choose concurrency from actual available CPU/memory/disk. Do not oversubscribe to the point that simulation wall time or host stability materially degrades. Record concurrency and host context in the campaign manifest.

## 7. Per-run completion contract

A run is formal only if:

```text
normal simulator exit
terminal gpu cycle recorded
Core SHA == FINAL_CORE_SHA
Framework runtime SHA == FINAL_FRAMEWORK_SHA
config/trace hashes match campaign manifest
parser succeeds
all required terminal invariants PASS
all required output schemas/artifacts exist
no stale/pre-fix result was reused
```

Mark valid runs only as:

```text
COMPLETE_VALID
```

Anything else remains failed/diagnostic until resolved.

## 8. Required per-run artifacts

At minimum retain:

```text
run_status.json
manifest.json
target_summary.csv
target_slice.csv
target_kernel.csv
target_bank.csv
target_window.csv
target_l1.csv
target_dram.csv
parser.stdout
parser.stderr
```

Compress or index large raw logs after validation. Do not delete evidence required to diagnose a failed run before the campaign is frozen.

## 9. Mandatory data coverage

The final dataset must support analysis of:

```text
performance/cycles
Tag-way need/block and reserved-set pressure
Line MSHR occupancy/need/full block
Descriptor occupancy/need/pool-full block
Per-address cap checks/block
Descriptor chain depth
WAD occupancy/full/hazard/lifetime
resident/pending/dirty/bypass payload roles
payload service vs capacity denial
bank logical/grant/conflict/wait, per-bank and operation class
L1D accesses/misses/resource blockers/bank conflict
MissQ
L2->DRAM FIFO
successful lower transactions and bytes
DRAM scheduler causal block and time-weighted occupancy
DRAM internal ReturnQ
per-slice DRAM->L2 FIFO
DRAM bandwidth utilization
5K temporal behavior
kernel interval behavior
```

## 10. Immediate parsing and validation

After each run completes:

1. parse it immediately;
2. validate terminal invariants and provenance;
3. mark `COMPLETE_VALID` only if all checks pass;
4. compress/index raw log;
5. update campaign status table.

This avoids discovering a systemic schema issue only after all long runs finish.

## 11. Failure policy during the campaign

Follow `CODEX_TARGET_GOAL.md` exactly.

Key rule:

- environment/transient failure with unchanged sources/configs: retry only the affected run;
- pure parser/analyzer/reporting fix that does not change simulator runtime or producer semantics: raw logs may be reparsed, but record separate runtime and analysis SHAs if they differ;
- any Core/runtime producer/config/architectural-timing change after formal runs begin: the previously completed formal runs are no longer one-source-pair evidence and must be quarantined; restart the formal 26-run on the new final pair after re-passing C7e acceptance.

## 12. Campaign completion

The campaign is complete only when:

```text
COMPLETE_VALID = 26/26
FAILED = 0
TIMEOUT = 0
all runs use one frozen runtime source/config pair
all mandatory final telemetry is present
all terminal invariants pass
```

The exact acceptance gate is in `FINAL_26RUN_ACCEPTANCE_CRITERIA.md`.

## 13. Aggregate outputs

Generate at least:

```text
TARGET_BASELINE_FINAL_STATUS.tsv
target_baseline_comparison.csv
target_resource_pressure.csv
target_blocking_matrix.csv
target_bank_pressure.csv
target_lower_path.csv
target_l1_pressure.csv
target_temporal_summary.csv
target_kernel_summary.csv
TARGET_BASELINE_BOTTLENECK_ANALYSIS.md
TARGET_BASELINE_CLOSEOUT.md
campaign_manifest.json
RAW_LOG_INDEX.tsv
SHA256SUMS
```

## 14. First-pass analysis discipline

`TARGET_BASELINE_BOTTLENECK_ANALYSIS.md` should answer, only from measured data:

```text
Does Tag/set allocation block?
Are 128 line MSHRs limiting?
Is the 256-descriptor pool limiting?
Does the 32/address cap bind?
Is WAD capacity or same-address ordering significant?
Is payload service/capacity limiting?
How much real Banked contention exists and where?
Does L1D become the limiting layer?
Which lower resource dominates: MissQ, L2->DRAM, scheduler, ReturnQ, DRAM->L2, bandwidth?
Which workloads show sustained vs bursty pressure?
How large is the isolated B0-Legacy -> B0-Banked effect?
```

Do not force a bottleneck label where evidence is weak. Use `NO_CLEAR_INTERNAL_BOTTLENECK` or `MIXED` when appropriate.

Do not claim RO/TVD/Unified opportunity magnitude yet; only identify which workloads/resources should be prioritized for the later shadow study.

## 15. Review pack and Codex -> ChatGPT handoff

Create a directly browsable final pack:

```text
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
```

Include the aggregate outputs above, representative parsed samples, manifests, validation summaries, source/config anchors, and SHA256SUMS. Exclude large raw logs; include `RAW_LOG_INDEX.tsv`.

Publish documentation-only mirrors to the permanent coordination branch:

```text
hrl/ep-l2-exp-v0
```

including:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/review_packs/FINAL_TARGET_BASELINE_850_r1/
```

`LATEST_REPORT.md` should state:

```text
Stage: Final Target Baseline @850 MHz
Status: PASS / FAIL
Final Core SHA
Runtime Framework SHA
Analysis Framework SHA if different
26/26 status
strongest measured findings
remaining issues
review-pack path
recommended GitHub files for ChatGPT
```

Then STOP before 1 GHz or Opportunity Study.
