# One-shot independent final audit

Run `python3 final_audit/audit.py` from the proposal pack once actual terminal
notification arrives. It writes only its own `AUDIT.json`. It does not wait,
loop, launch, accept, notify, mutate registry/lease or become another controller.

`IN_PROGRESS` means at least one endpoint/controller remains active, including
terminal validation/publication. Missing terminal evidence during this period
never becomes inferred exit0 or an application failure. Any independently found
invariant/evidence errors are still explicitly listed under `audit_errors`.

After all four endpoints and the original controller retire, the result is:

- `COMPLETE_PROVEN`: four independently accepted endpoints and two exact same
  main61 CURRENT_ACCEPTED pairs, published and actually delivered to D.
- `TERMINAL_NEGATIVE_OR_INCOMPLETE_PRESERVED`: exact terminal negative/incomplete
  receipt preserved and charged; no false accepted pair or automatic retry.
- `TERMINAL_EVIDENCE_ERROR`: contradictory/missing required evidence or protected
  ledger/resource contract violation requiring review.

The script checks published plan/spec/Q references against the pinned published
source tree and exact SHA; existing approval+scope guards cover old46, original
matrix/reservations/capacity10, accepted/HOLD,2+2 separate charges and no fifth.
Each endpoint's snapshotted approved spec, complete input audit, durable readiness
and direct-parent wait4 exit binding, native/collector/controller PID/start_ticks/
boot identities, whole instructions,64slice/hardware/resource closure and original
`runner.validate_terminal_summary` are independently reconciled. It reports actual
retained result bytes, cumulative10/24GiB generation and physical resources.

No large raw/trace content, main/archive or complete trace SHA is recomputed.
Exact raw SHA identity is compared between previously authenticated receipts and
terminal metadata. Main61's legacy terminal parser does not export a separate
per-kernel completion UID array. The audit accurately identifies its closure basis:
19 FWT or1 SGEMM trace manifest,791609344 or1658916864 total instructions, normal
actual native exit0, all_kernels termination and existing complete-input validator.
It does not invent a separate per-kernel runtime counter. Per-kernel analysis can
continue through D's existing accepted-evidence workflow.

Only syntax compilation was performed while the four native processes were
running. The actual final audit has deliberately not been repeatedly invoked.
