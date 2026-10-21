# Approved four-start central scope candidate

This directory contains review candidates only. No active utility, original
registry/CLIENT/lease/controller, native application, binary or Goal was changed.
Root E2 must review, publish/read back, activate the exact source manifest and
rebind CLIENT before adopting under the original permanent REGISTRY.lock.

Candidate files for integration at `util/ep_l2/mechanism_e/`:

- `workload_policy.py`: pure exact-four scope, approval/spec/input/profile guards;
  immutable old46 prefix, original buckets/matrix/runtime/accepted/HOLD records;
  append-only two batches of two attempts, no implicit retries/refunds.
- `limits_policy.py`: dispatch only the new exact workload scope to its own
  guard and approved null operational timeout. Original capacity path retained.
- `policy_v2.py`: exact workload condition/comparison branch; original matrix
  and generic native/profile qualification paths retained.
- `coordinator.py`: same permanent locked adoption, per-condition binding,
  independent SGEMM input adoption, and existing reserve/start/finish path.
  Physical gates, durable intent/parent wait and singleton controller unchanged.

## APIs

`workload_policy.operational_override(spec)` returns the exact approval-bound
runtime override. Preserve original `identity.termination_contract` timeout10800;
new `spec.timeout_seconds` is null, only for the approved four. The full spec is
canonical-SHA-bound except `input_audit` (inspector attaches it) and the operational
override (separately exact-checked). All paths, configs, parser, source, labels,
Q ID, profile and complete identity remain bound. Labels exactly match own Q;
F `oracle=True` is preserved, as it identifies the RO-manifest scope rather than
an idealized-data-service mode.

Use `Coordinator.adopt_workload_pipeline(APPROVAL_PATH)` once at the STOPPED
boundary; then `bind_workload_condition(spec)` appends qualified exact conditions.
FWT two can bind first, SGEMM own two later. Existing bindings cannot be changed.
SGEMM independent input adoption uses `adopt_workload_selection(path)` rather than
pretending it preceded the historical original32 selection deadline. Selection
is explicitly selected_by E / E_ADOPTION_OF_PRIOR_D_PREREGISTRATION and preserves
the original D proposal bytes/commit/SHA. Original seven selections remain.

`workload_pipeline_batches` is the sole added ledger field; no old reservations
are expanded. Every reservation still goes into the original attempts/runs.
Its condition ID, spec SHA and separate batch attempt ID are recorded atomically.
Failure and RESOURCE_LIMIT remain charged. A failed spawn also consumes its
condition opportunity, so it cannot silently create a fifth reservation/retry.

## Bounded control validation

`test_controls.py` exercises candidate actual APIs in temporary copies of the
central registry, with a non-executable fake binary and fake process object.
Live registry, raw files, native simulator and complete trace bodies are untouched.
Source-scoped controls must pass before activation. Prior failed control outputs
are retained as engineering evidence; they are not application starts or native
scientific qualification. Production `resource_gate`, unique_controller and
start/finish implementations are called rather than mirrored.
