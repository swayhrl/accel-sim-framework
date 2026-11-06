# Closed-only postprocess preparation V1

This is a CPU-only engineering package. It has not consumed, strictly accepted,
archived or restored any actual UUID. All 15 tests use `MOCK_NOT_SCIENCE` data.
There is no execute CLI. Running the module prints PREPARATION_ONLY.

## Component API

`with CloseoutSession(config) as session: session.finish(existing_cohort)`

Exactly one consumer thread owns the session. For a replacement owner image,
use `execution_mode=OWNER_IMAGE_CLOSEOUT`. The initial8 root and original
registered 32-start request are fixed. No remaining24 entry point exists.
Already-created RESULT files are adopted without rewriting and their original
true164 archive/native typed restore is verified again. New closure invokes the
same immutable `oracle_results.finish_evidence` with only the previously reviewed
alias552 and source-proven sparse dc00 private `wrap_consumer` hooks. `install()`
is never called. The component does not call parent/ops/model/front-end functions.

Main must provide an actual, independently reviewed admission verifier before
any execution. `CONFIG_TEMPLATE.json` is PENDING and cannot pass admission.

## Whole-flow exclusion and handshake

The session holds `BASE/control/OWNER_RECOVERY_AND_CLOSEOUT.lock` throughout the
closeout loop, covering strict, qualification, original archive and RESULT. Main
must acquire the SAME lock before ANY old-owner GIL recovery or image transition.
The old worker did not know this new lock; merely acquiring it does not prove
that the old worker cannot advance. An external worker requires an independently
reviewed live proof of real old-image quiescence. An exec replacement can instead
prove that the prior image/threads retired, while retaining actual PID/start and
lease/pipe continuity. These are actual admission predicates, not CPU mocks.

Bootstrap order avoids a lock handshake deadlock: if Main trigger holds this
lock, the replacement image first reports its lease/pipe-drain ACK with zero
closure/zero scientific launch, Main releases its lock, then the sole consumer
enters this session. Never wait for session acquisition before the bootstrap ACK.
Do not open and flock the same file a second time using a different OFD. This
component deliberately does not accept a caller's unverified inherited lock FD.

Do NOT externally hold the original per-cohort CLOSED_COPY lock or the target
receiver lock. The unchanged original archiver obtains those locks itself.
Resource/disk gates, SOURCE_KEEP and native restore all remain in that primitive.

## Admission interface

The config pins `admission_verifier={path,sha256}`. Its pure function
`verify_closeout_admission(context, config)` returns live, independently reviewed
facts. Context contains schema, stage_root, request, governance_lock, actual
caller_pid/start_ticks, execution_mode and `new_scientific_starts=0`.

Return bindings must match context, plus `status=PASS`,
`original_closer_threads_excluded=true`, `owner_recovery_excluded=true`,
`new_scientific_starts_permitted=false`,
`independent_quiescence_or_retirement_review=PASS`, monotonic observation and
expiry within 60 seconds. Include the real source/review/exec-entry/FD/thread
proof references. The session checks this before each cohort. Durable exclusion
over a long archive derives from retirement/governance, not from a short-lived
PID observation. `mtime`, lack of a current file lock, or an idle wchan alone are
insufficient. The verifier must not perform GIL/exec/signal or registry mutations.

The Main authorization reference must be an immutable actual release with
`status=AUTHORIZED_CLOSED_ONLY`, exact request, this runner SHA, exact verifier
reference, execution_mode, governance_lock and explicit
`authorized_closed_cohorts` (at most the original32). No example PASS release is
provided. The config also requires `actual_execution_authorized=true` and
`new_scientific_starts=0`.

## Evidence and integrity

Each processed row must already have consumed UUID + pinned INTENT + identical
DONE/execution_receipt/NATIVE_EXIT + original raw SHA, natural successful observed
termination and a no-longer-live original simulator. The original strict still
verifies compressed/decompressed raw, input/source/binary/libcudart/config271,
progress, lifecycle, counters and resource traces. A stopped/nonzero/unobserved
row is HOLD for this narrow runner, not silently promoted or resubmitted.

Actual closer PID/start, role, source/hook pins, original identities and closure
references go to separate immutable `BASE/control/CLOSED_POSTPROCESS_AUDIT`
BEGIN/END sidecars. Original simulator provenance is never relabeled as external
owner provenance. Original RESULT and strict files are not overwritten.
The registered request and original source identity are checked before/after.
Engineering errors stop the caller; no hidden automatic retry or model launch.
Any partial strict/archive evidence is retained for explicit same-UUID engineering
completion. Audit sidecars are engineering provenance, not new scientific IDs.

## Read-only source callgraph findings

* `initial8/tools/oracle_results.py:30` finish_evidence reads registered consumed,
  performs strict/qualification, original archive then exclusive RESULT creation.
* `oracle_native.py:22-46` registered/canonical/spec_for are read-only; registered
  validates exact plan/source/spec/budget evidence. `:47-51` ancestry is in
  assert_parent_lease, called by model prepare at `:109-111`, not this closer path.
* `oracle_strict.py:32-99` terminal calls registered/spec_for/check_input/binding;
  no prepare/run_native/update_authority or parent lease assertion is invoked.
* `oracle_outbox.py:21-41` proves the registered consumed, closed exact source;
  `:47-70` keeps original primitive and resource gates, no caller ancestry guard.
* `T/tools/sweep_outbox.py:80` archive owns CLOSED_COPY and global receiver locks;
  its last assert_parent_batch_or_closed_source override checks DONE/output UUID,
  not caller ancestry. These archive locks do not cover strict/qual/RESULT.
* Old `.install()` hook APIs enforce the original owner/Main thread. They are not
  used or bypassed here: existing pure module-private wrap_consumer APIs are used.

Full source pins and AST/source findings are in READONLY_SOURCE_AUDIT.json.
This review is not proof that the currently stuck old image can never resume.
That separate admission question remains HOLD until independently established.

## Scientific limits

No new model, dispatcher, register, request, UUID, budget mutation, reset, refund,
owner probe, signal, gdb, exec, GPU call, capture, CH Oracle or remaining24 release.
No production/source change. The Oracle remains a controlled model counterfactual,
not a mathematical upper bound or guaranteed realizable DTC gain. Raw missing
counters remain null; source-proven derived zero stays separately labeled. Input,
capture ELF, HtoD and full application numerical correctness limitations persist.
