# EP-L2 Motivation Instrumentation — ChatGPT Source Interim Review

Status: **FIX_REQUIRED_BEFORE_PILOT_PROMOTION**

This review is based on the pushed isolated source candidates:

```text
Core      a7125c72dd843c48e6a7512c42eb38fcad9d34c8
Framework 31a632d16db1939cf129921f2625b4bdc1ddbf05
branch    hrl/ep-l2-motivation-v0
parent Core      1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
parent Framework d61ffd23c926a25fa463a3e6e955c885b45f0f8a
```

The current `vectorAdd_4M` ON pilot may finish naturally. Do not kill it. However, current WBUF output is diagnostic-only until blocker 1 below is repaired; if Core semantics change, rerun the pilot under the corrected frozen source before promotion.

## 1. Mandatory semantic blocker — WBUF release is too late

ADR-009 defines one shadow WBUF slot as dirty-line/WB-packet data after WB packet creation **waiting for the per-slice lower interface to accept that packet**. It must be released at successful lower-interface acceptance, not at final WB completion and not after additional downstream queuing.

Current Core instead calls:

```text
L2_dram_queue_pop()
  -> ep_l2_motivation_record_wb_lower_accept()
```

only when `memory_partition_unit::dram_cycle()` has selected the subpartition, passed `can_issue_to_dram()`, passed DRAM scheduler admission, and pops the existing per-slice `m_L2_dram_queue` entry into the DRAM latency path.

That includes time already spent in the per-slice L2->DRAM FIFO and channel arbitration/scheduler behind the intended WBUF lifetime. It therefore overstates:

```text
active WBUF occupancy
WB creation->accept lifetime
WBUF4/8/16 projected would-block pressure
WB_PATH primary share when the shadow WBUF branch wins
```

### Required correction

Source-audit the real success point where the cache-side MissQ/memport transaction is accepted by `L2interface` into the per-slice `m_L2_dram_queue`.

Move the shadow WBUF release observation to that successful push/accept event for `L2_WRBK_ACC` only.

Do not change the real queue, WB, WAD, arbitration, or cache behavior.

Permanent directed evidence must distinguish:

```text
WB packet created        -> WBUF allocated
MissQ still waiting      -> WBUF live
L2interface accepts WB   -> WBUF released
WB waits in L2->DRAM Q   -> WBUF already free
DRAM issue               -> no second WBUF release
set_done                 -> WAD may finally release; not WBUF
```

The test should include a held/full L2->DRAM or downstream scheduler case proving that post-interface queueing does not extend WBUF lifetime.

## 2. Mandatory operational blocker — parser must stream raw logs

Current Framework parser materializes the entire raw log through:

```python
args.log.read_text(errors="replace").splitlines()
```

This is not acceptable for the broad campaign. The project has already observed multi-GB/19-GB raw logs where whole-file parsing creates excessive host RSS.

Replace this with a one-pass streaming parser over the file handle. Do not retain unrelated simulator lines in memory.

Requirements:

- exact same EPL2MOTV1 output as current parser on fixtures;
- duplicate application-slice records still fail closed;
- exactly 64 application slice records still required;
- malformed/duplicate fields still fail closed;
- source-log SHA256 may be computed with a second streaming pass or incrementally, but never by `read_bytes()` on a large log;
- record parser wall time / peak RSS on at least one pilot.

## 3. Required directed-test coverage is not yet present

The pushed Core delta currently changes production source but does not add the mandatory motivation directed regressions required by the acceptance contract.

Before pilot promotion, add permanent tests for at least:

### Reuse stack

- first touch;
- immediate repeat (distance 0);
- exact threshold pairs 8/9, 16/17, 32/33, 64/65, 128/129, 256/257, 512/513, 1024/1025;
- >1024 case;
- epoch reset;
- slice independence;
- nine-bin sum equals reuse_instances.

### Post-eviction

- clean real resident eviction;
- dirty real resident eviction;
- next re-reference matches correct block;
- no real hit/miss change;
- no stale/double-count state.

### WBUF

- creation increments active lifetime exactly once;
- corrected lower-interface acceptance releases exactly once;
- WBUF4/8/16 thresholds on one event stream;
- WAD remains allowed to live after WBUF release;
- terminal active WBUF state drains.

### Exclusive classifier

- SET_ASSOC-only;
- MSHR_META-only;
- MISSQ_LOWER-only;
- WB_PATH/WAD-only;
- WB_PATH/WBUF-shadow-only;
- at least two combined blocker priority cases;
- sum of five categories equals projected blocked cycles for C=4/8/16.

## 4. Source/documentation mismatch — post-eviction source map

Core `a7125c72` correctly extends post-eviction observation from dirty-WB events to any successfully committed valid victim by preserving `victim_block_addr` in preview and recording it after successful access.

Framework `SOURCE_MAP.md` still says `Real eviction = WRITE_BACK_REQUEST_SENT`, which is dirty-only and is now stale.

Update it to the actual valid-victim replacement commit point and document clean + dirty coverage.

## 5. Counter naming/semantics hardening

Current `wbuf_would_block` increments on each eligible frontend miss-admission cycle/attempt while:

```text
victim_dirty && active_shadow_wb >= C
```

It is not a count of unique dirty misses. Rename the parser-facing field/column to something such as:

```text
wbuf_trace_projected_would_block_cycles
```

or document that exact cycle/attempt semantics. Do not call it unique events.

For Figure 2, cycle accounting is the desired primary quantity.

## 6. Reuse-distance interpretation boundary

The implementation computes:

```text
# distinct more-recent 128-B blocks between consecutive references
```

with immediate repeat = distance 0. This is a valid stack-distance definition.

Keep current user-approved plotting bins if desired, but figure text must not claim that the `<=8` bin is exactly the hit fraction of an 8-entry fully-associative cache. Under this distance convention, an exact C-entry LRU capture condition is `distance < C`.

If later using reuse data as exact victim-cache-capacity prediction, emit a separate exact cumulative `distance < C` table.

## 7. Epoch-local unique-line semantics

The stack and touch map reset at kernel/epoch boundaries while cumulative application counters sum epoch-local observations. Therefore application-level:

```text
unique_lines
unique_lines_reused
one_touch_unique_lines
```

are sums of per-slice, per-epoch unique-line populations, not one global address-set deduplicated across the whole application.

Document this explicitly in FIELD_SEMANTICS / parser output labels. This is acceptable and consistent with the chosen no-cross-epoch reuse contract.

## 8. What already looks correct

Subject to directed-test confirmation:

- motivation telemetry is a separate default-OFF option;
- Core is a linear 2-commit descendant of the reviewed integrated parent;
- reuse stream is deduplicated against frontend retry cycles through the `seen_frontend` sidecar;
- L1/L2 writeback references are excluded from the reuse stream;
- block addresses are normalized to the 128-B L2 line;
- bounded MRU state keeps exact observed stack distance through 1024;
- WBUF capacities 4/8/16 are evaluated together without controller feedback;
- Figure-2 classifier is exclusive by construction and preserves `OTHER`;
- Core `a7125c72` fixes clean+dirty eviction observation rather than dirty-only reuse;
- Framework parser regression passes according to the Codex report;
- Release build passes according to the Codex report.

## 9. Pilot handling

Let the currently-running `vectorAdd_4M` ON pilot finish naturally.

Treat its output as:

```text
PRE_FIX_DIAGNOSTIC
```

for WBUF/WB_PATH if it used the late-release source.

Its reuse-distance data may be useful for debugging, but once Core changes for the WBUF release fix, rerun the final pilot suite on one frozen corrected source so the review package has one provenance pair.

Do not launch the remaining pilot/broad campaign until blockers 1-3 are closed and the corrected source passes Release + directed regressions.

## 10. Review state

```text
Source architecture direction:        CONDITIONAL PASS
Reuse collector source audit:          CONDITIONAL PASS pending directed tests
Post-eviction collector:               PASS in source, docs stale
WBUF source semantics:                  FAIL — release point too late
Exclusive classifier:                  CONDITIONAL PASS pending directed tests
Parser implementation:                 FAIL for broad-run robustness (whole-file load)
Broad motivation campaign:             NOT READY
```

Next requested state after repair:

```text
MOTIVATION_INSTRUMENTATION_PREFLIGHT_REVIEW_READY
```

At that point ChatGPT can re-review the corrected source/tests and, if clean, authorize pilot promotion and broad parallel launch.