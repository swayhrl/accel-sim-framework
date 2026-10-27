# Scan M16 typed engineering-negative evidence implementation V1

**Review candidate; Main is the sole production executor. No real scan archive, terminal certificate, authority/ledger mutation or signal has been performed by the implementing agent.**

Exact original: `E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1`, UUID `19105d9d-7522-498e-bf1d-73fbf7aba766`. It remains a spent engineering failure, not a completed performance result.

Pinned implementation: `08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013`. Qualification source: `b658c3d42c6e1fd2e42817134fa568342e44dff3b81aef00bfe33862b6b5ed07`. Native CPU qualification: **15 tests PASS**, including full archive→native ext4 restore→typed certificate→real verifier round trip on explicitly synthetic files, idempotence, archive tampering, partial chunk recovery, interrupted restore preservation and explicit new restore recovery, live/unknown generations and writer-FD rejection, immutable collisions, and small true164 metadata hardlink publication. The actual scan was inspected read-only; production scan copy/certificate has not run.

## Main commands

Use this **same fixed absolute module path** for execution and verification. Its path and SHA are themselves pinned in the evidence transaction; do not move it after execution.

```sh
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py --inventory
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/scan_m16_diagnosis_v1/terminal_impl_v1/scan_m16_engineering_negative_v1.py --execute --expected-self-sha 08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013
```

`--execute` requires the reviewed exact self SHA, native host/boot/namespace/device and true164 identity, exact spent intent and source pins, no original DONE/EXIT/execution receipt/result/standard archive receipt, and resource gates. Main should inspect stdout and preserve the returned verifier proof. A lock contention or observation error returns HOLD; it is not a model retry.

The final bundle is deterministic under:

`A/engineering_negative_evidence_v1/<exact-cohort>/<tx>/`

It contains `SOURCE_MANIFEST.json`, original outputs plus explicitly added `_ENGINEERING_CONTEXT` entries in hashed tar chunks, gzip CRC proof for **all gzip members including the legal perf alias**, departure proof, native restore proof, separate `ENGINEERING_ARCHIVE_RECEIPT.json`, and `ENGINEERING_TERMINAL_NEGATIVE.json`. All original output files and their paths remain untouched.

Native restore is confined to `R/analysis/engineering_negative_restore_v1/`. Interrupted restores are kept, never overwritten or recursively removed. Default resume accepts a fully verified existing restore; otherwise it HOLDS. Only Main can explicitly pass `--new-restore-attempt` to create one new absent owned destination. Completed recovery attempts can be reused; byte or metadata mismatches remain evidence. Abandoned partial temporary metadata collisions fail closed and require Main to preserve/resolve them explicitly.

## Verifier API for E and resource integrations

```python
module.verify_bundle(bundle_path, expected_self_sha="08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013")
# or
module.verify_certificate(certificate_path, expected_self_sha="08aecd21ba2dbea0656bd8e390acad09f4276954b2d1bc7dcbaec9593c74c013")
```

Only return status `VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED` is usable. It includes exact cohort/UUID, certificate SHA, actual archive SHA, native2128 restore identity, two fresh actual departure scans, `verified_future_model_growth_bytes=0`, `accepted_cycles=None`, `performance_accepted=False`, original spent1/refund0 and `original_native_execution_receipt_present=False`.

Each verification rechecks current authority/INTENT binding without writes, source pins, full original lstat/file SHA inventory, all original/restored gzip CRCs, complete archive chunks and SHA, full native restore numeric metadata/bytes/alias semantics, and **two full /proc environment and FD scans** separated by ≥1 second. Any unreadable environment/FD/proc hole fails closed; no generic errors become RSS zero. Known strace-related PIDs must be absent, even if later PID reuse would be plausible. The gate can therefore HOLD conservatively on unrelated PID reuse rather than guessing ownership.

The certificate has schema `L2_MLP_ENGINEERING_TERMINAL_NEGATIVE_V1`, state `ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY`; accepted cycles/wait returncode remain **null**, actual signal delivery is `NOT_DIRECTLY_OBSERVED`, frontend returncode is the independently observed2, scientific/performance acceptancefalse, spent1/refund0/automatic_retryfalse, sourcekeep. It expressly states `original_done_present=False`, `original_exit_present=False`, `original_registry_execution_receipt_present=False`. Scientific identity binds frozen input/trace/Core/Framework/binary/config/expected options and original DH/M16; source identity binds native boot/namespace/device.

This implementation writes no standard `_ARCHIVE_RECEIPT`, original RESULT, DONE, EXIT, native execution receipt, authority or budget field. It implements no new trial registration and no 350-cell statistical substitution. E may expose an explicitly verified typed analysis view preserving the original raw row; Main alone may separately qualify a resource overlay recognizing this evidence.

## Qualified dependencies and resource accounting

The original outbox `libraries()` loads source-pinned frozen `full_result_bundle`/V9 primitives. This implementation reuses only `RangeWriter`, archive verification and native restore/check primitives. It does **not** weaken or call the original scientific DONE-based manifest gate. The standard receiver flock remains exclusive. Its private RangeWriter instance uses a new evidence-copy resource gate; no existing module/controller is patched.

Restore bytes plus16MiB must fit the already reserved unfinished failed-generation write allowance; all peer/native future writes and metadata floors remain checked. The actual-source inventory has 19 entries and47 source/runtime/config/context pins; two real departure scans found every known related PID absent and no generation environment/writer-FD/permission holes. `READONLY_INVENTORY.stdout.json` and its run record bind the source SHA and timestamps. All originals remain SOURCE_KEEP; freeing growth or publishing any science result requires Main's separate verified integration.

Known inherited library issue: the frozen native restore reader emits a Python ResourceWarning for an unclosed **read-only** archive chunk handle. CPU byte/metadata/CRC checks still pass; the one-shot worker closes descriptors on process exit. Frozen library source was not changed. A future low-level cleanup can be separately qualified; it is not suppressed or presented as a failed scientific run.
