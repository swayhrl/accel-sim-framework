# REAL_MODEL_TRACE_INPUT_CONTRACT

`REAL_MODEL_TRACE` is the only admission class for H's future scientific
pipeline.  The Retry570 NVBit 1.8 parser material in this directory is a
fixture qualification, not a model trace and cannot satisfy this contract.

## Required input schema

The producer supplies a JSON object with
`schema_version = C16_REAL_MODEL_TRACE_INPUT_V1` and all of the following:

- `trace_kind = REAL_MODEL_TRACE` and `scientific_model_evidence = true`;
- `terminal_status = COMPLETE`;
- `producer.g_producer_commit`: exact 40-hex G producer commit;
- `producer.nvbit18_tool_sha256` and `producer.c16_tracer_sha256`;
- exact `identity.model`, `model_revision`, `package`, `package_revision`,
  `scenario`, and `scenario_input_sha256`;
- one or more `raw_artifacts`, each with `remote_path`, local `raw_path`,
  remote/local sizes, remote/local SHA-256 values, and
  `remote_local_sha256_closed = true`.

Each artifact's remote/local size and SHA must be identical.  Fixture labels,
fixture booleans, partial terminal states, model-family-only identity, naked
kernel ordinals, or a missing tool hash are rejection conditions.

The executable validator is:

```bash
python3 util/vm_tlb/c16/lane_h/real_model_trace_contract.py \
  --input /outside-git/G_REAL_MODEL_TRACE_INPUT.json \
  --expected-g-producer-commit <exact-G-commit> \
  --output /outside-git/REAL_TRACE_PIPELINE_CANARY.json
```

Its only success result is `REAL_TRACE_PIPELINE_CANARY`.  It permits integrity
checks, a single-trace parser canary, storage accounting, and registration of
compact artifacts.  It expressly forbids cross-model, family-level, or causal
scientific conclusions at this point.

## Raw ingest and retention contract

Raw material stays outside Git.  The required transition is:

```text
remote raw
  -> immutable remote size/SHA receipt
  -> rsync local .partial
  -> local size/SHA closure
  -> immutable ingest receipt
  -> optional zstd/xz + compressed size/SHA receipt
  -> hash-verified parser scratch
  -> hash-closed compact derived artifact receipt
```

`c16_nvbit_raw_ingest.py` implements the transition.  It has no remote-delete
operation; it never deletes a local raw file; and it quarantines failed or
partial transfer/compression/scratch files under `failed/`.  Receipts are
exclusive-created and made read-only.  Consequently remote raw cannot be
removed before local SHA closure, and compression closure cannot be mistaken
for authorization to remove local uncompressed raw.

Example (the `LOCAL` transport exists only for automated fixture tests):

```bash
python3 util/vm_tlb/c16/lane_h/c16_nvbit_raw_ingest.py probe \
  --local-root /data/c16_nvbit_raw --remote-host user@gpu-host \
  --remote-path /data/captures/trace.raw --run-id <run> \
  --target-identity <model-package-scenario> --tool-identity <tool-shas>

python3 util/vm_tlb/c16/lane_h/c16_nvbit_raw_ingest.py ingest \
  --local-root /data/c16_nvbit_raw --remote-facts /data/c16_nvbit_raw/receipts/REMOTE_FACTS_<sha>.json \
  --compression zstd
```

## Storage-canary input

After admission, form `C16_NVBIT_STORAGE_CANARY_INPUT_V1` from the closed
receipts and include the admission's
`status = ADMITTED_REAL_TRACE_PIPELINE_CANARY` and
`pipeline_mode = REAL_TRACE_PIPELINE_CANARY`.  It requires `trace_kind = REAL_MODEL_TRACE`,
`scientific_model_evidence = true`, a `canary` object with `raw_bytes`,
optional `compressed_bytes`, `trace_file_count`, `kernel_count`, optional
`memory_record_count`, `capture_duration_seconds`, and `source_batch_size`,
plus optional `storage.local_available_before_bytes`.

Run:

```bash
python3 util/vm_tlb/c16/lane_h/c16_nvbit_storage_estimate.py \
  --input /outside-git/REAL_MODEL_STORAGE_CANARY.json \
  --output /outside-git/NVBIT_STORAGE_ESTIMATE.json
```

The output records raw/compressed size, ratio, counts, duration,
bytes/record, free space before/after, B4/B8/B12/B24/B48 storage-only
projections, and a scratch-aware safe campaign budget.  A fixture can exercise
the schema only with `--allow-fixture-test`; its projections and campaign
budget are deliberately `null`.
