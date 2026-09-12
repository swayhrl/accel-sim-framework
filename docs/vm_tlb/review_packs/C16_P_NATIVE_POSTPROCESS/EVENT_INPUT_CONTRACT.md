# C16-P event-driven input contract

P is dormant after this checkpoint. It resumes only for a complete P1, P2, or P3 event. A partial event is recorded as `INPUT_NOT_HASH_CLOSED` and does not enter formal postprocess.

## P1 — new G `.nsys-rep`

Required immutable fields are: producer G full commit SHA and producer manifest path/SHA; deployment, scenario, input, and profile-run identity; raw report path, byte size, SHA-256, and an explicit transfer receipt binding source and local destination path/size/SHA; G Nsight Systems version and export command/config identity; and profile terminal status plus package/runtime identity needed to check the report against its producer receipt.

P verifies raw SHA before local export, uses the qualified local CLI, checks schema/population, preserves every parsed launch, and emits the full catalog, `PROFILE_REPORT_INDEX`, `RAW_ARTIFACT_INDEX`, `RUN_JOIN_AUDIT`, compact timing/kernel summaries, deterministic gzip, and a hash manifest. Parse errors or non-catalogued rows are explicit failures; they are never silently dropped.

## P2 — G direct semantic diagnostic

Required fields are diagnostic producer commit/manifest/hash, diagnostic run/report identity, evidence type, direct module/NVTX identity, and a diagnostic launch table or semantic `.nsys-rep` whose rows contain report-local structural identity. Accepted evidence types are only `DIRECT_RUNTIME_NVTX`, `DIRECT_MODULE_ID`, or `UNKNOWN`.

P will publish `DIRECT_SEMANTIC_MAP.tsv` with clean deployment/scenario/report identity, diagnostic report/run identity, report-scoped structural identity, `layer_id`, `operator`, evidence type/source, and ambiguity status. `KERNEL_NAME_HEURISTIC` is forbidden. A clean launch with zero or multiple eligible diagnostic matches remains `UNKNOWN`.

P also publishes time-weighted semantic coverage: launch count and mapped-launch fraction, total and mapped GPU duration, mapped GPU-time fraction, ambiguous duration, and UNKNOWN duration. A 95% GPU-time target is not a license to classify UNKNOWN rows.

## P3 — tiny NVBit canary

Required fields are producer commit, run/target identity, raw path/size/SHA, transfer receipt, schema/version, and terminal status. P performs only transport, hash, and schema checks. Lane H owns final address/memory-fingerprint interpretation.

## Local export qualification policy

P is `LOCAL_NSYS_EXPORT_QUALIFIED_FOR_CURRENT_TOOL_PAIR`: current remote Nsight 2024.1.1 and local Nsight 2024.2.3 passed frozen S1 semantic-structure/population qualification. SQLite bytes need not match. Requalify only if G/local Nsight version, report schema, export command, or consumed field set materially changes.

Large `.nsys-rep`, SQLite, raw TSV, and deterministic gzip remain outside Git. Git tracks only compact index/manifest metadata, logical artifact IDs, sizes, hashes, producer/run identity, compression method/version, and row counts.
