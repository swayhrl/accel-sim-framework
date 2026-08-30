# EP-L2 Motivation — WBUF Lifecycle Accounting Fix Handoff

Status: **AUTHORIZED — observation-only correctness repair required before preflight can pass**

## 1. Trigger

The corrected final-provenance `vectorAdd_4M` Motivation-ON run on:

```text
Core      2f9d984cc25422353bdf0270c6c27c82502f77c9
Framework 549e3db7b87d2c51686e2ca2435994be770df88e
```

reports:

```text
wb_packets_created              = 24251
wb_packets_lower_accepted       = 24187
wb_packets_terminally_outstanding = 64
```

while the existing real L2 resource-leak check is clean.

The frozen candidate therefore cannot be promoted to `MOTIVATION_INSTRUMENTATION_PREFLIGHT_REVIEW_READY`.

## 2. Scientific interpretation

Do not assume this is an undrained simulator queue.

The accepted WBUF contract remains:

```text
allocate: real L2 dirty-victim WB packet creation after payload readout
release:  successful cache-side L2interface acceptance into the per-slice L2->DRAM queue
```

`set_done()` is not WBUF release.

This stage fixes only observation-side lifecycle accounting. It must not alter actual cache, WB, WAD, lower-queue, arbitration, or DRAM behavior.

## 3. Root-cause audit — mandatory before patching

Before choosing a fix, determine why exactly 64 created lifetimes have no matched lower-accept accounting.

Audit at minimum:

1. whether the final application snapshot is emitted after the real L2 resource-leak check/drain point;
2. actual `m_ep_l2_motivation_active_wb` cardinality at the final snapshot, per slice;
3. create-side identity/address and lower-accept-side identity/address for unmatched lifetimes;
4. whether the mismatch is caused by:
   - raw-vs-block-normalized address;
   - WB request type/path mismatch;
   - create/release ordering;
   - address-key collision/reuse;
   - an unobserved lower-accept path;
   - snapshot timing;
   - another source-proven cause;
5. whether the one-per-slice pattern is deterministic.

Preserve a small extracted diagnostic table for the 64 unmatched final lifetimes; do not commit a huge raw log.

## 4. Preferred lifecycle identity

WBUF models **WB packets**, not addresses.

Prefer an exact WB transaction identity for shadow lifecycle tracking:

```text
WB packet / mem_fetch identity or an observation-only monotonic WB token
```

so create and lower-accept match the same physical simulated transaction.

An address-keyed implementation is acceptable only if source evidence proves all of the following:

- the key is normalized identically at create and release;
- no two simultaneously live WB packets can share the key;
- WAD/order semantics guarantee that uniqueness for every production path;
- sequential reuse of the same address cannot collide with stale observation state.

Do not merely change one side to `block_addr()` without proving these conditions.

## 5. Required telemetry/invariants after the fix

Add enough observation-only evidence to make lifecycle closure independently auditable, including at least:

```text
wb_packets_created
wb_packets_lower_accepted
wb_active_at_snapshot
wb_active_max   (recommended)
wb_lifetime_sum/max
```

At a true naturally drained terminal snapshot require:

```text
wb_packets_created == wb_packets_lower_accepted
wb_active_at_snapshot == 0
```

The parser may fail closed if the true terminal application snapshot violates this.

Kernel/shared snapshots are allowed to contain live WBs and must not be subjected to a false terminal-zero rule.

## 6. Permanent directed regressions

Add source-level/production-path or faithful permanent directed tests covering at minimum:

1. one dirty victim: create exactly once, release exactly once at `L2interface::push`;
2. WAD remains live after WBUF release until its own completion point;
3. two different simultaneous WB packets track independently;
4. same line written back twice sequentially does not collide with stale shadow identity;
5. address/sector normalization cannot prevent release matching;
6. 4/8/16 active-count behavior remains correct after identity repair;
7. multi-slice lifecycle state remains isolated;
8. natural terminal drain leaves zero active WBUF shadow entries;
9. motivation OFF/ON cycles/instructions and existing B0/L1/DRAM/M0a outputs remain exact.

## 7. Provenance after repair

A source fix necessarily creates a new Core SHA. That is authorized.

Once the observation-side fix and tests pass:

- freeze one new final Core/Framework provenance pair;
- rebuild Release;
- rerun all final preflight pilots required by the accepted motivation contract on that exact pair;
- do not mix the old `2f9d984c...` pilot outputs into formal paper-facing tables;
- retain them only as `PRE_WBUF_LIFECYCLE_FIX_DIAGNOSTIC`.

The final pilot set must include the required OFF/ON controls and all four production pilots from the existing acceptance criteria.

## 8. Scope boundary

This repair does not authorize:

- functional physical WBUF behavior;
- counterfactual WBUF4/8/16 performance simulation;
- Unified/RO/TVD mechanism behavior;
- broad motivation campaign before corrected preflight review;
- changing the accepted reuse-distance or exclusive blocker definitions except where required to keep them timing-neutral and consistent with the lifecycle fix.

## 9. Deliverables

Publish:

```text
docs/ep_l2/review_packs/MOTIVATION_WBUF_LIFECYCLE_FIX_r1/
  README.md
  ROOT_CAUSE.md
  SOURCE_ANCHORS.md
  CHANGED_FILES.md
  VALIDATION_SUMMARY.md
  UNMATCHED_PRE_FIX_SAMPLE.tsv
  POST_FIX_LIFECYCLE_EVIDENCE.csv
  FINAL_PILOT_STATUS.csv
  RAW_LOG_INDEX.tsv
  SHA256SUMS

docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md
```

Then regenerate/update the normal preflight pack.

## 10. Stop condition

Stop and request ChatGPT review only when the repaired frozen provenance reaches:

```text
MOTIVATION_INSTRUMENTATION_PREFLIGHT_REVIEW_READY
```

with all terminal lifecycle invariants closed and no broad campaign launched.
