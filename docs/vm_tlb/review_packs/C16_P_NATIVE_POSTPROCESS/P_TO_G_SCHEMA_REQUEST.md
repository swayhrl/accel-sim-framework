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

## Cross-lane boundary

This is a schema-only request. It carries no performance, memory, output,
population, kernel, or semantic outcome metric. Prospective AWQ-holdout
catalogs remain `HOLDOUT_PENDING_FREEZE` and `C_FORBIDDEN` until C publishes an
exact selector-freeze SHA. P's train/tune priority remains Llama, Qwen0.5, and
Qwen7 raw.
