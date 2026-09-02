# Local frozen-model staging

Status: `RUNNING`.

The active local-snapshot authorization replaces the historical remote
Hugging Face credential transport requirement. The source snapshot is
`/workspace/model/meta-llama__Llama-3.2-1B_main`; it is not committed to Git.

`LOCAL_MODEL_SOURCE_MANIFEST.json` records the six necessary Transformers
files, their byte sizes, and SHA256 values. Its primary BF16 safetensors file
is `2,471,645,608` bytes and hashes to
`68a2e4be76fa709455a60272fba8e512c02d81c46e6c671cc9449e374fd6809a`, the
previously independently checked LFS object for
`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.

The only approved destination is
`/root/autodl-tmp/m4a-llama/models/Llama-3.2-1B-frozen`. The remote copy must
contain the identical manifest and every listed file must reproduce the
source SHA256 before a workload is launched. Native `original/` checkpoints,
duplicates, and unrelated caches are excluded.

Pending actions: resumable transfer, remote hash verification, then an
explicit local-only loader/preflight validation. No model workload or trace
has run under this resumed authorization yet.
