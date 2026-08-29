# C6 B0-Banked arbitration audit

Status: **AUDIT FAIL for performance attribution; no source change made.**

This is a source-level and directed audit of the 22-of-26 interim data.  The
four `scan`/`3mm` runs remain live and are deliberately excluded.  The current
B0-Banked performance comparison is not valid architecture evidence until the
accounting and idle-bank admission issue below is corrected and the affected
runs are repeated.

## Finding

`ep_l2_payload_store::request()` in
`src/gpgpu-sim/gpu-cache.h:2153-2206` makes an idle-bank first attempt a
pending operation and returns `false`.  On the *next* cycle,
`gpu-cache.h:2160-2174` promotes the oldest pending op to `m_granted`; only a
retry of the same op can consume that grant (`gpu-cache.h:2188-2193`).  The
initial failure unconditionally executes `++m_bank_conflicts`
(`gpu-cache.h:2198-2206`).

Therefore every logical Banked payload op has an unconditional staging/retry
cycle, even when its bank is idle and there is no older pending operation.
This does **not** exist in B0-Legacy: the 1R1W path returns true to the first
available port user (`gpu-cache.h:2177-2182`).

`bank_requests` counts calls/attempts (`gpu-cache.h:2187`), not logical
operations. `bank_grants` counts successful consumption of a selected pending
op (`gpu-cache.h:2191`). `bank_conflicts` counts every `request()` false
return, including the mandatory first idle-bank staging failure; it is not a
true same-bank-contention count.

The EPL2B0V1 `block_payload`/`block_bank` counters have the same attribution
problem. Failed fill readiness increments both in Banked mode
(`src/gpgpu-sim/l2cache.cc:944-951`), and any payload-enabled
`l2_cache::access()` `RESERVATION_FAIL` increments `block_payload`, then
unconditionally increments `block_bank` for mode 2
(`l2cache.cc:1145-1149`). These are failed access/fill attempts, not a
predicate that established true same-bank contention. Snapshot emission simply
exports those counters (`l2cache.cc:1468-1489`).

## Directed trace (temporary non-repository harness)

The harness invoked `ep_l2_payload_store` directly against Core
`200cb485c2fe27a7b0a867d2f173b63582fcaece`:

| Case | Cycle N | Cycle N+1 | Later | Attempts / conflicts / grants | Result |
|---|---|---|---|---|---|
| isolated resident ID 0, bank 0 | `false`; pending=1; 1 / 1 / 0 | retry `true`; pending=0; 2 / 1 / 1 | — | 2 / 1 / 1 | idle op misclassified as conflict; unconditional +1 cycle |
| IDs 0 (bank 0) and 1 (bank 1), same cycle | both `false`; 2 / 2 / 0 | both retry `true` in same cycle; 4 / 2 / 2 | — | 4 / 2 / 2 | independent banks grant concurrently, but only after structural staging |
| IDs 0 then 4, both bank 0, same cycle | both `false`; 2 / 2 / 0 | retry younger ID 4 `false`, then older ID 0 `true`; 4 / 3 / 1 | ID 4 `true` at N+2; 5 / 3 / 2 | 5 / 3 / 2 | older wins; the younger observation/retry is also called a conflict |
| ID 0 older pending; ID 4 arrives next cycle, same bank | ID 0 `false`; 1 / 1 / 0 | ID 4 `false`, ID 0 `true`; 3 / 2 / 1 | ID 4 `true` at N+2; 4 / 2 / 2 | 4 / 2 / 2 | older pending op wins correctly |

The existing `tests/ep_l2/test_payload_banked.cc` proves oldest sequencing and
cross-bank parallel grants, but it does not test idle-bank first-cycle grant or
counter semantics; that is why the structural accounting behavior survived.

## 11-pair bookkeeping audit

See [target_banked_arbitration_audit_11pairs.csv](target_banked_arbitration_audit_11pairs.csv).
For 8/11 workload pairs exactly:

```text
attempts = 2 * grants
reported_conflicts = grants
```

This is the deterministic signature of one staging failure/retry for every
logical operation, not evidence that half of all logical operations collided.
`cfd_097k` has 28,280 attempts/conflicts beyond that baseline, `sad` has 2,
and `FWT_7_21` has 52.  Those residuals can contain true contention or
additional retries, but current counters cannot separate them.

## Exact correction proposed (not implemented)

1. Preserve per-bank pending queues and the existing oldest-sequence selection
   for any bank that has an older pending/granted op.
2. In `request()`, if the target bank has no older pending/granted op and has
   not already consumed its one operation in the current cycle, grant the
   first logical operation immediately.  Do not enqueue it, return `true`, and
   increment only the grant/logical-operation counter.
3. If an older pending/granted op exists, enqueue newer work with its original
   sequence and deny it; a same-bank operation after a grant in the same cycle
   is likewise a true contention/retry. This preserves one op/bank/cycle,
   cross-bank parallelism, and oldest-ready fairness.
4. Split telemetry into `bank_logical_ops`, `bank_attempts`, `bank_retries`,
   `bank_true_conflicts`, and `bank_grants`.  Do not reuse
   `bank_conflicts` for staging.  Split `block_payload` from actual bank
   contention, or add a distinct `block_bank_true_contention`.
5. Add the four directed cases above as permanent C6 regressions. Expected
   post-fix result: isolated idle-bank operation grants at cycle N with zero
   true conflict; different banks grant concurrently at N; same-bank work
   contends once; older pending work wins.

No simulator source has been changed in this audit.
