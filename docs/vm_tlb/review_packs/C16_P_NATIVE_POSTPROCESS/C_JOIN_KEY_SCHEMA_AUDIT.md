# C16-P → C join-key and schema audit

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL`.

Scope: this audit uses the two local copies whose raw-report and remote-export
SQLite SHA-256 values are bound by G's `CENSUS_EXPORT_VALIDATION.json`. It is a
schema readout only, not a cross-lane scientific input: G's formal native
producer checkpoint has not yet been committed. Local `nsys export`
qualification subsequently passed and the audited population was regenerated
from P-local SQLite exports.

## Result

The complete S1/S2 population has all Lane-C kernel-catalog fields required by
`C16_DATA_AND_PROVENANCE_CONTRACT.md`:

`run_id, deployment_id, scenario_id, phase, decode_step_bin, device, context,
stream, correlation_id, launch_ordinal, kernel_name, implementation_key, grid,
block, start_ns, end_ns, duration_ns, operator_class, layer_id, shape_key,
dtype_key, semantic_evidence, mapping_status`.

The current emitted population is 169,920 rows (S1 56,720; S2 113,200). There
are zero empty required fields and zero duplicate C join identities over
`run_id + device + context + stream + correlation_id + launch_ordinal`.
Every row retains `operator_class=UNKNOWN` and `layer_id=UNKNOWN`; no semantic
label was inferred from the kernel name.

The P schema can also produce the five payload types C requires to admit a
future committed catalog: `KERNEL_CATALOG.tsv`, `KERNEL_SEMANTIC_MAP.tsv`,
`SEMANTIC_COVERAGE.tsv`, `NATIVE_BASELINE.tsv`, and
`RUNTIME_IMPLEMENTATION_AUDIT.tsv`, plus `HEAVY_TAIL_KERNELS.tsv`.

## G handoff: no missing C join columns, but closure metadata is needed

No additional launch/catalog columns are required from G before future C
selection. Please publish these closure items with G's formal producer
checkpoint before C consumes this material:

1. a committed producer manifest listing each raw `.nsys-rep`, size and
   SHA-256, its run UUID, package ID/commit/manifest SHA, GPU/driver/runtime
   identity, and the compact catalog payload hashes;
2. an explicit transfer receipt that records both the AutoDL source path/SHA
   and local destination path/SHA. The currently available export-validation
   receipts bind the local raw report SHA, but the `CENSUS_NSYS_RECEIPT.json`
   artifact field has `output_sha256: "NA"`, so that file alone is not an
   independently auditable dual-endpoint transfer receipt;
3. Nsight Systems CLI version/config in the producer checkpoint. This binds
   P's compatible local-export qualification to the remote export; and
4. direct runtime mapping evidence if operator/layer or runtime-KV-layout
   labels are desired. Without it P will preserve `UNKNOWN` and C must
   stratify it explicitly.

## Storage boundary

The full 134,253,922-byte TSV and deterministic 5,110,532-byte gzip remain
outside Git under `artifacts/c16_p_native_postprocess/local_exports_provisional`.
`RAW_INDEX.tsv` and `POSTPROCESS_MANIFEST.json` there bind logical row counts,
paths, sizes, and SHA-256. This provisional directory must not be passed to
Lane C as a selector input.
