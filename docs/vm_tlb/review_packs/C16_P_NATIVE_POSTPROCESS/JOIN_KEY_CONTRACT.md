# C16-P join-key contract

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL`.

This contract is derived from the actual local S1/S2 catalog, baseline, raw artifact index, and run-join audit. It defines a Lane-C review input only; it does not authorize selector freeze while direct semantic evidence and G's formal producer checkpoint remain absent.

## Actual source schema

`KERNEL_CATALOG.tsv` has 169,920 physical launch rows. Its identity-relevant fields are `run_id`, `deployment_id`, `model_id`, `model_revision`, `tokenizer_revision`, `scenario_id`, `input_hash`, `device`, `context`, `stream`, `correlation_id`, `launch_ordinal`, `implementation_key`, `shape_key`, and `dtype_key`.

`PROFILE_REPORT_INDEX.tsv` binds every catalog `run_id` to immutable raw `.nsys-rep` SHA-256 (`profile_report_id`), raw byte size/path, local SQLite identity, local tool version, and source validation-receipt SHA. It is the mandatory bridge from a launch row to a report. `NATIVE_BASELINE.tsv` has a separate `run_id` plus `measurement_kind` and `measurement_index`.

## A. Deployment, scenario, and input identity

Catalog-level deployment identity: `deployment_id + model_id + model_revision + tokenizer_revision + implementation_key + dtype_key`.

The current catalog has no per-row `quantization` field. It must be obtained from a hash-bound profile/producer receipt and never backfilled into launch rows. The current source receipts specify `NONE`.

Scenario/input identity: `scenario_id + input_hash`. `shape_key` is an observed structural field, not a substitute for scenario/input identity.

## B. Run and repeat identity

`KERNEL_CATALOG.run_id` identifies the profiled run represented by one report after joining `PROFILE_REPORT_INDEX`; it is not interchangeable with `NATIVE_BASELINE.run_id`.

Current S1 and S2 each have one profiled run and a separate unprofiled baseline run with three measurements (`measurement_index` 0, 1, and 2). Baseline repeat key: `baseline run_id + measurement_kind + measurement_index`.

Those three measurements are repeated observations of one logical scenario, not three additional profiled launch populations. The physical launch view retains every CUDA launch. The logical workload-instance view groups baseline repeats by `deployment_id + scenario_id + input_hash` and leaves C to choose a repeat/estimator policy explicitly.

## C. Profile/report identity and report-local IDs

`profile_report_id` is the raw `.nsys-rep` SHA-256 from `PROFILE_REPORT_INDEX`, with producer `run_id` retained as a consistency check. SQLite SHA is export-instance provenance only because a valid re-export need not be byte-identical.

`stream` and `correlation_id` are report-local. They are prohibited as cross-report join keys by themselves. The current real reports prove the risk: both use `CUDA_STREAM_7` and share 4,501 correlation IDs across distinct reports.

## D. Physical launch identity

Audited physical launch key: `profile_report_id + run_id + device + context + stream + correlation_id + launch_ordinal`.

Within a report, the reduced catalog key `run_id + device + context + stream + correlation_id + launch_ordinal` has zero duplicates. The raw report SHA is required at every cross-file or cross-report boundary. `launch_ordinal` is report-local, assigned from actual SQLite ordering (`start`, then SQLite `rowid`), and cannot join across reports without report scope.

A future direct semantic diagnostic retains its own report/run-local launch key. P may map it to a clean launch only through the event contract; an ambiguous structural match remains `UNKNOWN`.

## Automated audit and acceptance

`RUN_JOIN_AUDIT.json` SHA-256 is `bb14fd46fe276a3be17f91c45233f760b8fb8fc86e2d941d6e1b10a93dd4c00e`. It automatically checks required catalog key fields, nonempty values, complete SQLite population preservation, zero duplicate physical keys, one hash-closed report per profile run, baseline-repeat key uniqueness, and observed cross-report stream/correlation collisions.

It passed with 169,920 catalog rows, zero rows with an empty required key field, zero duplicate physical launch keys, zero duplicate baseline repeat keys, and one explicit cross-report collision pair. Naked `correlation_id` or `stream` joins are thus rejected by contract.

The compact Git-external `PROFILE_REPORT_INDEX.tsv` and `RAW_ARTIFACT_INDEX.tsv` hashes are `982f83b5ddfeb3e0561840fb8b6a8bbccfa25c52980d013b9bbb6eec796be73f` and `4a72b166533856806d8b35d95bd2ab75dfb6e80189a3e8ed7cacb7ab1fd95502`.
