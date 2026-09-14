# Validation

| Check | Result |
|---|---|
| Recovery publication commit and manifest SHA | PASS: commit `2e955e007bcabcd3ec24a5f9d24768d27caaee27`; manifest SHA256 `0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc` derived from its committed blob |
| Six source raw SHA256 and size | PASS: exact `RAW_ARTIFACT_INDEX.json` paths, hashes, and sizes verified |
| Six canonical-copy SHA256 and size | PASS: every destination equals its source/index digest and size |
| RAW_CTA parser canary | PASS: CTA/warp prefix excluded from PC selection; Prefill `0x650`, Decode `0x110` |
| Target identity and record counts | PASS: three Prefill 8192; Decode2/3/4 64; explicit GLOBAL target opcodes matched |
| Decode overlap | PASS: pairwise and three-way exact/32B/64B/128B/4KiB/64KiB/2MiB SET_ONLY relations emitted |
| Prefill boundaries | PASS: reproducibility and phase comparison are count/structure-only; no prohibited absolute-VA relation |
| Parser directed tests, pycompile, TSV audit, diff check | PASS; commands recorded in the parent H validation record update |
