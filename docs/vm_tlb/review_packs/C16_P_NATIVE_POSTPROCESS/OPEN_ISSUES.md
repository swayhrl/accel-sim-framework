# C16-P open issues and boundaries

1. **G producer checkpoint pending.** P's inputs are hash-closed through the
   available receipts, but G has not committed the formal native producer
   checkpoint/manifest. Keep every P payload `REAL_NATIVE_SCHEMA_SANITY /
   PROVISIONAL`; C must not freeze a selector from it.
2. **Explicit dual-endpoint transfer receipt not located.** The available G
   export-validation receipts bind local report SHA-256, while the remote
   profile receipt's artifact SHA field is `NA`. P requests a committed
   transfer receipt with remote path/size/SHA and local path/size/SHA.
3. **No direct operator/layer mapping evidence.** All operator/layer labels are
   `UNKNOWN` and semantic mapped-time coverage is zero by design. Kernel-name
   strings and NVTX phase ranges are not promoted to semantic labels.
4. **Runtime-KV layout remains unknown.** The runtime audit preserves direct
   attention/compile/quantization receipt fields but does not infer layout.
5. **Raw retention.** Raw reports, local SQLite files, the 134 MB launch TSV,
   and gzip are retained outside Git and indexed. Do not delete the sole local
   hash-verified copy. Future NVBit canaries are transport/schema-only work for
   P; H owns memory-fingerprint interpretation.
