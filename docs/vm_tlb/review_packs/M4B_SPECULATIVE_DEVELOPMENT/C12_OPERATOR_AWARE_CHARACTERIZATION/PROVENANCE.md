# C12 Operator-aware provenance

Consumed formal C12 source commit: `269c274712f4eeaee15d304033a9e6d61b5b3206`.
Only rows marked terminal `PASS` in both ARM_STATUS.tsv and ARM_RESULTS.tsv were parsed.

## Frozen execution identity

- framework_anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- core_head: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- binary_sha256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`

## prefill

- C12 F0 compute-only list: `/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/prefill/f0/traces/kernelslist.g`
- list SHA-256: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` (692 entries)
- semantic derivative: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/prefill-semantic/compute-only-kernelslist.g` (byte-identical)
- raw semantic manifest: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/prefill-semantic/semantic-full-kernel-manifest.json`; raw COMPUTE filtering exactly recreates C12 list (NCCL removal has no index shift)
- runtime sidecar: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/m4a-llama-prefill-20260902T182016Z/allocation-sidecar.json`; weight base `0x7fd99e000000`, size `1012011008`, 146 non-overlapping parameter ranges

## decode1

- C12 F0 compute-only list: `/workspace/vm-m4b-speculative/c5-results/C11_AUTHORIZED_NOT_RUN/decode1/f0/traces/kernelslist.g`
- list SHA-256: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` (740 entries)
- semantic derivative: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/decode1-semantic/compute-only-kernelslist.g` (byte-identical)
- raw semantic manifest: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/decode1-semantic/semantic-full-kernel-manifest.json`; raw COMPUTE filtering exactly recreates C12 list (NCCL removal has no index shift)
- runtime sidecar: `/workspace/vm-m4b-stage-f96b7ea9-5bdd4b55/m4a-llama-decode1-20260903T004138Z/allocation-sidecar.json`; weight base `0x7f7ec6000000`, size `1012011008`, 146 non-overlapping parameter ranges
