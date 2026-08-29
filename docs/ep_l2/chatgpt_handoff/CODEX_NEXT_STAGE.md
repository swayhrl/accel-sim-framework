# EP-L2 ChatGPT Handoff — CODEX_NEXT_STAGE

Status: **C6d PASS; C7d reviewed as CONDITIONAL PASS / NOT READY for final 26-run.**

Read first:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/C7E_DISCUSSION_REFERENCE.md
```

## Objective

Complete one final instrumentation/readiness stage:

```text
C7e Final Target-Characterization Readiness
```

This must be the **last source-changing stage before the clean 13 x 2 @850 MHz Target-Baseline campaign**.

C7e is instrumentation/provenance only. Do not change modeled architecture behavior or timing semantics.

## Source bases and isolation

Derive C7e from the reviewed C7d final pair:

```text
Core base:
88e243e8e421002079adc85b9efae3452c02a828

Framework base:
2aef9fad48207415a9697f9b891068b42008e0a8
```

Create independent branches/worktrees, suggested:

```text
Core:      hrl/ep-l2-c7e-final-char-v0
Framework: hrl/ep-l2-c7e-final-char-v0
```

Do not modify or reuse previous C6d/C7d runtime directories as formal C7e evidence.

## Out of scope

Do not change:

```text
L2 geometry or replacement
MSHR/descriptor capacities or lifetime
WAD functional semantics
payload capacities or ownership
C6d bank arbitration semantics/timing
L1 configuration
queue capacities
DRAM scheduler/timing parameters
850 MHz primary target
Unified borrowing
RO mechanisms or oracle
TVD
1GHz experiments
```

---

# 1. L1D target telemetry — mandatory

C7d only exposed a helper for native fail-reason totals; it did not produce an L1D-only application/kernel Target record.

Add a **GPU-scope L1D-only timing-neutral telemetry path**, preferably a separate schema such as:

```text
EPL2L1V1
```

Do not duplicate GPU-global L1 metrics into every L2 slice.

Aggregate **L1D only**, not L1I/L1C/L1T.

At minimum emit application cumulative and kernel launch-to-completion deltas for:

```text
L1D accesses
L1D misses
LINE_ALLOC_FAIL
MISS_QUEUE_FULL
MSHR_ENTRY_FAIL
MSHR_MERGE_FAIL
MSHR_RW_PENDING
L1D bank/latency-queue conflict
```

Use exact existing native fail classes when semantically valid.

For bank pressure, source the existing real L1D bank/latency-queue conflict event (the path that increments `gpgpu_n_l1cache_bkconflict`) or an equivalent exact timing-neutral counter. Do not infer bank pressure from generic `RESERVATION_FAIL`.

If practical, add eligible/need denominators for the major L1D resource failures; if not, exact event counts plus accesses are acceptable for this stage, but document the limitation.

Parser output should include:

```text
target_l1.csv
```

with explicit scope/kernel UID/start/completion/overlap semantics.

---

# 2. Correct Tag/set denominator semantics

Preserve C7d compatibility fields, but do not use `c7d_line_alloc_eligible` as the final Tag-way denominator because it includes `SECTOR_MISS`.

A sector miss on an already-resident 128B line does not require a new Tag way.

Add exact fields, suggested:

```text
c7e_tag_way_alloc_need
c7e_tag_way_alloc_block
```

where `tag_way_alloc_need` represents a true new-line/new-way allocation attempt only.

`tag_way_alloc_block` must correspond to the exact all-reserved/no-replaceable-way condition.

The final analyzer should use these C7e fields for Tag/set blocking ratios.

---

# 3. Fix MSHR / descriptor / per-address denominator semantics

Keep the exact C7d blocker fields:

```text
c7d_line_mshr_full_block
c7d_descriptor_pool_full_block
c7d_per_address_cap_block
```

Add independent **need/demand** denominators that do not depend on which `full_reason()` won priority:

```text
c7e_line_mshr_need
    = request semantically needs a new line MSHR

c7e_descriptor_need
    = request semantically needs one persistent requester descriptor

c7e_per_address_cap_check
    = request is merging into an existing address chain and therefore checks the 32/address cap
```

Do not suppress one denominator merely because another resource is simultaneously the selected blocking reason.

Document whether blocker events are mutually exclusive by `full_reason()` priority while need denominators are independent.

---

# 4. WAD kernel lifetime semantics

C7d application WAD lifetime totals are useful, but kernel snapshot fields currently read cumulative `l2_cache` lifetime totals.

Choose one correct solution:

### Preferred

Make completed-WAD lifetime statistics true launch-to-completion deltas for kernel records.

### Acceptable fallback

Mark WAD lifetime fields explicitly application-only and emit `NA` / unavailable in kernel records.

Do not label cumulative application lifetime as a kernel interval metric.

---

# 5. DRAM/lower-path semantic repair — mandatory

The final campaign must distinguish issue attempts from successful issues and must keep the channel internal ReturnQ separate from the per-slice DRAM->L2 FIFO.

## 5.1 Issue attempts vs successful issues

C7d currently increments `dram_read_issues` / `dram_write_issues` when an L2->DRAM head is inspected, before actual acceptance.

Preserve compatibility fields if needed, but add clearly named exact fields:

```text
DRAM issue/head attempts
actual successful read issues
actual successful write/WB issues
actual successful read bytes
actual successful write bytes
```

Increment successful issue counters only at the production point where the request actually leaves the L2->DRAM arbitration and enters the DRAM-latency/DRAM path.

Use `mem_fetch::get_data_size()` (or the exact transferred request size used by production) for bytes; do not assume all transactions have the same size.

## 5.2 Separate return structures

The following are distinct and must remain distinct in telemetry:

```text
A. DRAM internal ReturnQ (per channel)
B. per-slice DRAM->L2 FIFO (`m_dram_L2_queue`)
```

Do not call a `dram_L2_queue_full()` condition `DRAM ReturnQ full`.

Add exact names/counters for each.

## 5.3 Scheduler blocking semantics

Separate at least:

```text
scheduler_full_observed
scheduler_causal_block
```

where causal block means the request could otherwise issue (no prior return-path/credit blocker) but the scheduler queue is full.

If overlapping resource-unavailable observations are also useful, retain them under explicitly non-causal names.

## 5.4 Channel-scope time-weighted occupancy

C7d scheduler occupancy is sampled when an L2->DRAM head is inspected; that is request/opportunity-weighted, not a DRAM-cycle average.

Add a **channel-scope** timing-neutral DRAM telemetry path, preferably separate from per-slice EPL2B0V1, e.g.:

```text
EPL2DRAMV1
```

At minimum record per channel over DRAM cycles:

```text
scheduler occupancy avg/p95/max
scheduler full cycles
internal ReturnQ occupancy avg/p95/max
internal ReturnQ full cycles
successful read/write issues
successful read/write bytes
native/verified bandwidth-utilization numerator + denominator or exact derived utilization
```

Application cumulative is mandatory. Kernel deltas are strongly preferred if low-risk. Do not duplicate one channel value into both subpartitions and later sum it as if independent.

Parser output should include:

```text
target_dram.csv
```

## 5.5 5K temporal windows

Current C7d windows already include:

```text
line MSHR
descriptor
WAD
resident payload
MissQ
L2->DRAM FIFO
bank logical/conflict/wait
```

Add channel-level 5K windows for at least:

```text
scheduler occupancy/full
internal ReturnQ occupancy/full
successful DRAM read/write bytes or bandwidth utilization
```

if this can be implemented with bounded host overhead.

---

# 6. Analyzer/schema cleanup

Update parser/analyzer to make semantic labels match producer meaning exactly.

At minimum fix or avoid the following current issues:

```text
`dram_bandwidth_util` must no longer be NOT_EMITTED if C7e produces/parses exact utilization.

Do not name a wait-cycle field `*_events`.

Do not name an occupancy average `*_events`.

Primary bank conflict rate remains:
  bank_true_conflict_ops / bank_logical_ops
```

Add analysis-ready columns for:

```text
Tag-way need/block ratio
Line-MSHR need/full-block ratio
Descriptor need/pool-full-block ratio
Per-address-cap check/block ratio
WAD full/hazard/lifetime
Payload service denial vs capacity denial
Bank true-conflict rate and wait
L1D exact blockers
MissQ / L2->DRAM
DRAM scheduler causal block + occupancy
internal ReturnQ
DRAM->L2 FIFO
actual lower read/write transactions + bytes
bandwidth utilization
```

Retain unavailable values as explicit `NOT_EMITTED...` rather than guessing.

---

# 7. Final formal runner hardening

Before the final 26-run, the runner must fail fast if the source pair is not exactly the reviewed final pair.

Add explicit expected-SHA support, e.g.:

```text
--expected-core-sha
--expected-framework-sha
```

or an equivalent immutable campaign manifest.

Before launch require:

```text
actual Core HEAD == expected Core SHA
actual Framework HEAD == expected Framework SHA
Core worktree clean
Framework source worktree clean
formal overlay/config hashes match campaign manifest
```

Do not merely record the current HEAD after launch.

Use a fresh final result root, e.g.:

```text
docs/ep_l2/target_baseline_results_final_850/
```

Do not reuse `target_baseline_results_c5c`.

---

# 8. Final-SHA validation — mandatory retained evidence

C7e cannot close based only on source review.

On the final C7e source pair retain compact evidence for:

```text
full Release build
complete C3-C7 + C6d + C7e directed/integrated regression set
parser regression
analyzer regression
Tag/MSHR/descriptor denominator directed tests
L1D aggregation tests
DRAM issue-attempt vs successful-issue tests
internal ReturnQ vs DRAM->L2 distinction tests
channel occupancy/window tests
kernel-delta tests
terminal invariants
git diff --check
clean source worktrees
```

## Timing neutrality

Run one natural short/medium workload with instrumentation OFF vs ON on the **exact final source pair**.

Compare exactly:

```text
gpu_tot_sim_cycle
sim instructions (or equivalent terminal instruction count)
L2 accesses/misses
actual DRAM read/write transaction counts
selected native functional/timing counters
```

They must match exactly except for telemetry output and host wall time.

## Host overhead

Measure host runtime overhead on the same natural workload. Prefer at least 3 OFF and 3 ON repetitions and report median wall time if practical; otherwise report the limitation and host-load context.

## Natural parsed sample

Retain at least one natural final-SHA parsed sample that actually contains completed 5K windows.

Also retain a final-SHA sequential multi-kernel sample proving application/kernel delta semantics for L2, bank, L1D, and any kernel-scope DRAM fields.

---

# 9. Readiness gate

After all C7e work, create a formal checklist answering YES/NO:

```text
C6d correctness frozen?
C7e Tag denominators exact?
C7e MSHR/descriptor denominators exact?
WAD scope semantics correct?
L1D application/kernel telemetry available?
DRAM issue attempts vs actual issues separated?
internal ReturnQ vs DRAM->L2 separated?
channel scheduler/BW telemetry available?
5K temporal coverage sufficient?
parser/analyzer aligned?
final-SHA build/regressions retained?
final-SHA OFF/ON timing neutrality PASS?
host overhead measured?
runner expected-SHA fail-fast PASS?
source worktrees clean?
```

End with exactly one recommendation:

```text
READY_FOR_FINAL_26_RUN
```

or

```text
NOT_READY_FOR_FINAL_26_RUN
```

Do **not** launch the 26-run until ChatGPT reviews this closeout.

---

# 10. Codex -> ChatGPT handoff routing

The permanent coordination branch is:

```text
Framework hrl/ep-l2-exp-v0
```

Stage source remains on the C7e implementation branch, but at closeout Codex must also publish the **documentation-only** handoff artifacts to the coordination branch so ChatGPT has one stable entry point.

At minimum mirror/push to `hrl/ep-l2-exp-v0`:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
```

Do not merge C7e source code into the coordination branch merely to publish docs.

`LATEST_REPORT.md` must point to the stage branches and exact final SHAs.

Do not modify ChatGPT-owned files under:

```text
docs/ep_l2/chatgpt_handoff/
```

---

# 11. Deliverables

Create a directly browsable review directory:

```text
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
```

with at least:

```text
README.md
FORMAL_RUN_READINESS.md
SOURCE_ANCHORS.md
COMMIT_HISTORY.md
CHANGED_FILES.md
C7E_TELEMETRY_SOURCE_MAP.md
C7E_SCHEMA.md
C7E_FIELD_MATRIX.csv
C7E_SEMANTIC_FIXES.md
VALIDATION_SUMMARY.md
OPEN_ISSUES.md
RAW_LOG_INDEX.tsv
SHA256SUMS
validation/
samples/
```

Large raw logs/build artifacts must not be committed.

Commit with explicit scoped paths only; do not use `git add .` or `git add -A`.

Push Core/Framework C7e branches, then publish the documentation-only `codex_handoff` + review pack to `hrl/ep-l2-exp-v0`.

Finally report only:

```text
final Core SHA
final Framework SHA
C7e branch names
READY/NOT READY
coordination-branch LATEST_REPORT path
review-pack README path
remaining blocker, if any
```

Then STOP before the final 26-run.
