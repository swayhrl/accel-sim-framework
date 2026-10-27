# Scan DH-M16 engineering failure diagnosis V1

Captured UTC: 2026-10-27T16:31:03.282706+00:00. Read-only inspection; zero launches, signals, retries, original-file changes or registry updates.

## Authoritative identity and outcome

- Cohort: `E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1`; workload `6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39`; input `6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39`.
- Actual execution UUID: `19105d9d-7522-498e-bf1d-73fbf7aba766`.
- Actual simulator PID/start: `1775705 / 985330216`; launcher `1775700`. Both `/proc` handles were absent at inspection.
- INTENT, LAUNCH, PID/maps and 12,000+ seconds of runtime samples prove that this was a consumed actual model execution. It was not a zero-start failure.
- Frontend returned code 2 with `Unterminated string starting at: line 20 column 11 (char 3203)`.
- `NATIVE_EXIT.json`, qualification DONE and registry execution receipt are absent. Raw, progress and resource gzip streams validate completely but end mid-application.
- Last telemetry seq `1251`, completed `621166305`, phase `SIMULATE`, end `NONE`. No natural terminal record exists. Latest recorded original policy decision was CONTINUE with zero cgroup OOM events.
- Keep **SPENT_ENGINEERING_PRESERVE / no retry**. It is impossible to restore a valid natural completion receipt from these artifacts. No accepted cycles can be extracted for the full input.

## Failure mechanism and evidence strength

1. Runtime resource sampling reads all unfinished generations' `NATIVE_SIMULATOR_PID_AND_MAPS.json` through unguarded `json.loads` in `resource_accounting_v1.rss()`.
2. The publisher serializes a full JSON byte string, then opens the final path with `xb`, writes, flushes and fsyncs. The path is visible before the write has completed; publication is not atomic.
3. The nearest new PID/maps write is `/root/data/dtc_l2_mlp_exploration_20261027_v1/DTC/run/results/6be4ff29-93dd-46bd-ae19-c440f064d2e8/NATIVE_SIMULATOR_PID_AND_MAPS.json`, SHA `b88bb618262214af8e6b05f502cb952fa2b230116ff236e65a3f0179d6ade6f1`, 11661 bytes. Its mtime is only `0.142003` seconds before the failed scan frontend log. It belongs to `E2-DTCL2MLP-769e6d9fd5f9cd53-DH-Q128-V1`.
4. Its maps string opens at exactly line 20, column 11, character 3203. Reading a 4096-byte or 8192-byte prefix reproduces the exact reported parser exception; the complete file parses normally. See `CAUSAL_EVIDENCE.json`.
5. An escaping resource-sample exception takes `run_native` through its `finally` cleanup, whose source sends SIGKILL to an unfinished process group, closes lossless gzip streams, and then propagates the exception before the receipt code. This source path explains why all logs are closed, no receipt exists, and neither handle remains. There is no preserved syscall record of the supervisor signal, so the exact signal delivery is source-derived, not directly observed.

**Limitation:** The failing frontend preserved only the JSON exception text, without traceback filename or the original partial byte buffer. The concrete peer UUID is therefore a high-confidence temporal/byte-position association. Do not report it as a uniquely observed culprit.

## Minimal preventative implementation proposal (not applied)

For future new workers only, qualify atomic publication of PID/maps metadata: write a unique hidden same-directory temporary file, fsync it, link to the final path with exclusive EEXIST semantics, fsync the directory, and remove only that owned temporary link. Do not touch INTENT/authority publication or existing workers. This protects existing readers from future half-published PID files without changing their source or policy.

If adding a read-side retry, restrict it to qualified per-generation PID metadata and bounded partial JSON reads. Never convert arbitrary parser errors to RSS=0 or erase unresolved growth reservations. All immutable source pins and historical scientific identities remain unchanged.

Main must decide any separately registered validation identity; never reuse this spent identity or overwrite its outcome. Ordinary read-only extraction can describe partial progress but cannot manufacture a terminal scientific result.

## Evidence bundle

`FACTS.json` records all original evidence paths, byte lengths, mtimes and SHA-256 values; `evidence/` holds preserved originals, immutable sources and matching peer PID snapshots. `CAUSAL_EVIDENCE.json` records exact source lines and CPU-only prefix reproductions. Raw logs stay on true164 and should not be committed to GitHub.
