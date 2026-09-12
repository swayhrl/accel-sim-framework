# C16 GPU package readiness — not yet published

Status: `WAITING_INPUT`; this file is deliberately not a
`C16_GPU_PACKAGE_MANIFEST.tsv`, `EXPECTED_HASHES.tsv`, or `TRANSFER_PLAN.md`.
The common contract permits publication of those three artifacts only after the
required offline gates are available as fixed producer commit plus manifest and
hash.  G and C now satisfy their respective release closures, but H has no
hash-bound publication; package publication remains blocked.

| Required gate | Required producer payload | Fixed published commit/manifest | A status |
| --- | --- | --- | --- |
| C16-0.3 | G environment/wheel/bootstrap lock | `b5039e…`, manifest `97b54c7c…`, 11 payloads PASS | PASS (offline only) |
| C16-0.4 | G runner/wrapper identity | `b5039e…`, manifest `97b54c7c…`, source-package SHA rows PASS | PASS (offline only) |
| C16-0.8/C | C offline parser/selector release | `fed28d…`, manifest `20b94eef…`, 22 payloads PASS | PASS (offline only) |
| C16-0.8/H | H offline parser/fingerprint release | commit `65b535…` has no manifest | WAITING_INPUT — not consumed |
| C16-0.2 | A model assets | this lane's `MODEL_ASSET_MANIFEST.tsv` | PASS |
| C16-0.6 | A token receipts | this lane's `INPUT_CORPUS.tsv` and `TOKEN_RECEIPTS/` | PASS |
| C16-0.7 | A scenarios | this lane's `SCENARIO_MATRIX.tsv` | PASS |

The only local runtime dependency prepared here is the CPU tokenizer verifier
(`transformers==4.51.3`, no Torch/CUDA).  It is not asserted to be a GPU runtime
or a substitute for G's environment lock.  Full non-Llama weights remain absent
locally by design and therefore no rsync command is authorized yet.  GPU rental
should remain paused until these fixed inputs close or the user explicitly
changes the authorization.
