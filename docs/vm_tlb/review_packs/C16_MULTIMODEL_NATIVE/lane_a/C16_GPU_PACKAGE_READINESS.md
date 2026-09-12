# C16 GPU package readiness — local preparation continues

Status: `ROLLING_P0_P1_P2_P3_PUBLISHED_WAVE2_30B_BACKGROUND_ACTIVE`. Immutable
P0--P3 are independent deployment transfer deltas. Each contains its own
package manifest/identity hash, `C16_GPU_PACKAGE_MANIFEST.tsv`,
`EXPECTED_HASHES.tsv`, and `TRANSFER_PLAN.md`; none authorizes runtime
execution or converts Wave-2 assets into an RTX3090 package.

| Required gate | Required evidence | Current result | Package consequence |
| --- | --- | --- | --- |
| C16-0.2 / Wave-1 | Local Llama3.2-1B, Qwen2.5-0.5B, Qwen2.5-7B raw, and Qwen2.5-7B AWQ checkpoint files, each with local path, byte count, SHA-256, model revision, and tokenizer revision | PASS. All raw (4/4) and AWQ (2/2) checkpoint files have immutable size-plus-single-SHA receipts and present local paths. | Closed for P0--P3 transfer-package publication only; a remote LFS declaration was never substituted for a local file. |
| C16-0.3 / C16-0.4 | Fixed G environment/wheel/bootstrap/runner release with every manifest path resolvable and hashed | PASS at `G@45e293b84940ef59b7b134bcda48aca7d0b99b2f`, manifest `7c18c2a8…`: 17/17 release payloads plus 66/66 local wheel SHA-256 checks pass. | Gate closed as CPU-only offline infrastructure; it neither runs nor authorizes a GPU workload. |
| C16-0.8 / C | Fixed C selector release | Final-consumed at `C@29e669eca19ac3b2a1350bf2d097569a41f123e1`, manifest `14a7c029…`, 24/24 payloads pass. | Offline selector protocol only, not a native fact table. |
| C16-0.8 / H | Fixed H hardening release | Final-consumed at `H@932c6fa44a4896265214fc2136e34698402a5c7f`, manifest `b7821231…`, four code payloads plus test receipt pass. | Offline admission protocol only; no dynamic H data are present. |
| C16-0.6 / C16-0.7 | Frozen inputs, actual CPU tokenizer receipts, and frozen scenarios | Available, hash-validated local A artifacts. | Will be incorporated only into the final package. |

P0 binds the fully verified Llama3.2-1B model/tokenizer revision
`4e20de362430cd3b72f300e6b0f18e50e7166e08`, fixed G/C/H commits and manifests,
and G's wheelhouse-manifest SHA-256. Its package manifest SHA-256 is
`ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f`.
It is suitable only for a separately authorized Llama transfer/import/canary;
P0 itself starts no GPU process. Each later full model closure must create a
new P-numbered delta without editing P0.

The already verified Qwen2.5-0.5B is separately closed as immutable
`packages/C16_GPU_PACKAGE_P1/`, whose package manifest SHA-256 is
`d8ac3ca44c4344b9a5fa752ba5a6549c007e901b26b426c9713b4d7e8749eb84`.

Raw Qwen2.5-7B is immutable `packages/C16_GPU_PACKAGE_P2/`, with all four
checkpoint receipts at revision `a09a35458c702b33eeacc393d103063234e8bc28`
and package-manifest SHA-256
`c937590dd4ea2b4f6407db7d8b077ed263af3cbc14562ef34142aa834b133f26`.
AWQ Qwen2.5-7B is independently immutable `packages/C16_GPU_PACKAGE_P3/`,
with two checkpoint receipts at revision
`b25037543e9394b818fdfca67ab2a00ecc7dd641` and package-manifest SHA-256
`704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c`.
Neither delta modifies P0/P1, includes Qwen3-30B-A3B, or starts execution.

Wave-2 does not block Wave-1: an existing local DeepSeek-V2-Lite checkpoint is
being prepared for file-level validation and Qwen3-8B remains non-blocking.
With the user-authorized 85 GiB start gate met, Qwen3-30B-A3B now has one
serial low-priority resumable download worker.  It has a 15 GiB pause guard,
records only whole-file size+SHA-256 matches as local assets, and cannot alter
P0/P1 or form an RTX3090 Wave-1 package. See
`QWEN3_30B_A3B_DOWNLOAD_POLICY.md`. No GPU, CUDA model execution, profiler,
NVBit, simulator, SASS, or full-ROI run is authorized or performed by this
lane.
