# C16 Qwen3-30B-A3B Asset Archive V2 — fail-closed review

Final decision: `QWEN3_30B_A3B_CANONICAL_ARCHIVE_FAIL_CLOSED`.

The actual discovered source layout is `metadata/Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/` with 16 safetensors shards, plus `runtime/immutable_verified_receipts/`, `runtime/status/`, `runtime/logs/`, and `runtime/pids/`.  The entire source root has 37 regular files and 0 symlinks.  The resolved candidate payload root is `/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Identity state binds `Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.  The actual shard count is 16 and the total is 61066575648 bytes; the historical 61066575648-byte anchor matched: `True`.  Independent source whole-file SHA-256, all 16 receipts, and all safetensors headers: `PASS`.

No source `model.safetensors.index.json`, `config.json`, or tokenizer authority files exist.  Thus HF index/tensor-map closure and offline exact-revision reconstruction cannot be proven without prohibited substitution from a cache/network.  No canonical archive was promoted at `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` and no historical snapshot was created at `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/qwen3_30b_a3b_download_v1`, because doing so would create false archive/provenance claims.

Unknown files: none; the non-model files are classified as receipts, state, or logs.  Source cleanup readiness is `DO_NOT_DELETE_OR_MOVE`.  Future node109 provisioning remains deferred; when an accepted canonical source exists it should be copied from node164 through `.partial` with independent rehash.
