# C16-P request: complete hash-bound P1 metadata

Status: `SCHEMA_REQUEST_ACTIVE / NO_RERUN_REQUESTED`.

P has locally verified the raw/report/receipt closure available from the new G1
checkpoints. The checkpoints bind producer commit, report identity, remote and
local raw path/size/SHA, terminal status, export command, package/runtime
identity, and local-returned receipts. They currently omit two immutable P1
fields required by P's frozen `EVENT_INPUT_CONTRACT.md`:

1. The exact remote `nsys --version` output used to create and validate the
   report.
2. A separately named raw-transfer receipt with its path and SHA-256, binding
   the remote source and local destination path, size, and SHA-256.

These fields should be added only in a new exact G producer checkpoint or a
named P1 event manifest. Do not rewrite old receipts, rerun a scenario, or
change model/runtime/scenario identity merely to satisfy this request.

## Requested event shape

The G P1 checkpoint/manifest should bind the following fields directly:

```json
{
  "producer": {
    "commit": "<full G commit>",
    "manifest_path": "<repository path>",
    "manifest_sha256": "<sha256 of exact bytes>"
  },
  "identity": {
    "deployment_id": "...",
    "scenario_id": "...",
    "input_hash": "...",
    "run_id": "..."
  },
  "nsys": {
    "version": "<verbatim nsys --version>",
    "profile_command": ["..."],
    "export_command_or_config_identity": "..."
  },
  "raw_transfer_receipt": {
    "path": "<local receipt path>",
    "sha256": "<receipt sha256>",
    "remote": {"path": "...", "size_bytes": 0, "sha256": "..."},
    "local": {"path": "...", "size_bytes": 0, "sha256": "..."}
  }
}
```

The checkpoint's existing report/receipt hashes and independent export evidence
remain necessary; this request does not replace them. P will re-audit the same
frozen local raw copy when these fields are published.

## Newly observed P1 S3 raw: publish the binding manifest before P consumes it

G commit `cc4e1023bef4a1536367329a54724b9eaf62d064` added a raw-index entry
for deployment `c16_qwen25_05b_native_reference`, S3 run
`a67d9a5e-049a-401f-bdbe-6281e89b7351`, with raw SHA-256
`80c7dcf4c99b7e8e7f9741a990e5429aa84895d2e6a7790d1a0a82facafdc08b`.
This is valuable transport evidence, but that commit changes only the runtime
status and raw index. It does not publish a P1 producer manifest or bind the
report to the required profile, export-validation, transfer, and immutable
Nsight-version receipts. P therefore classifies this input
`INPUT_NOT_HASH_CLOSED` and will not export it yet.

Please publish one immutable P1 event/checkpoint for this existing frozen raw
report, with the fields above plus the exact paths/SHA-256 values for the
profile receipt, binding/validation receipt, and remote validation SQLite when
one was used. This requests metadata only: do not rerun, substitute a scenario,
or alter the Qwen0.5 identity. Once the manifest is pushed, P can immediately
verify the existing raw copy and perform the local export/catalog/join audit.

## Cross-lane boundary

This is a schema-only request. It carries no performance, memory, output,
population, kernel, or semantic outcome metric. Prospective AWQ-holdout
catalogs remain `HOLDOUT_PENDING_FREEZE` and `C_FORBIDDEN` until C publishes an
exact selector-freeze SHA. P's train/tune priority remains Llama, Qwen0.5, and
Qwen7 raw.
