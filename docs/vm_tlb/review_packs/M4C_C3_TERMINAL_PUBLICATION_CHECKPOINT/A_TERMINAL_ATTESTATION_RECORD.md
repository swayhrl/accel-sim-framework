# A terminal attestation record

The external attestation is intentionally kept in the immutable formal C3
scratch root, not copied into Git:

`/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`

Its SHA-256 is
`891ad0d952f80400055c5075a5512dc7435d9fbd4a3ca98ce201ff2124f1191f`.
Its first line is exactly `A_TERMINAL_CONFIRMED`.

The attestation was issued only after a fresh, non-overwriting `--require-level
2` eight-arm summarization passed. It records C3 terminal completion and its
frozen binary/runtime anchors. It does not certify host PSI, the in-progress
v6 locality analysis, C4 completion, or eligibility for Window B/C work.

The runtime identity is the Core-local `libcudart.so` with SHA-256
`fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a`.
The earlier host-CUDA path record is superseded by the direct `/proc` mapping
evidence in `M4C_C3_PROGRESS_REVIEW_20260907/C3_RUNTIME_PROVENANCE_SUPERSEDING_RECORD.tsv`;
no formal manifest or result was rewritten.
