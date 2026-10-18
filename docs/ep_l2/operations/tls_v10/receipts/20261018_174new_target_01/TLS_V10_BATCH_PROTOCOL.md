# TLS-V10 target/source agreement proposal

This is an engineering handshake proposal, not COPY_READY or source-release approval. The exact executable parameters and acknowledgment order are in `TLS_V10_TARGET_BATCH_PROTOCOL_PROPOSAL.json`. Source must explicitly agree on Git-backed frozen manifest/root/txid and resource PASS before staging.

Use the unchanged V9 chunk receiver with one raw chunk per READY, at most 128 MiB of data and 256 MiB total physical bridge staging. Each chunk gets real164 close/reopen SHA and independent native chunk restoration. Chunk receipts explicitly say CHUNK_RANGE_ONLY; they never claim an incomplete original file is restored. Both sides acknowledge the exact chunk before its bridge payload is cleaned.

Once every range in a frozen group is accepted, finalize every original file and restore the complete group into a new absent native tree with the unchanged V9 all-file native restore implementation. Verify every original byte and numeric file/directory metadata. Join these complete proofs to the original frozen inventory. No samples, SSHFS projected ownership, or chunk-only proof can replace full original restoration.

The proposed target-only 24 GiB tmpfs is a native verification workspace; it avoids consuming the roughly 4.6 GiB of disk headroom above the 48 GiB floor. It is volatile and never the archive. A small native metadata probe, current memory/cgroup checks, projected capacity, and the source independent Lane/resource PASS must precede scientific use. No original or verification tree deletion is proposed; only exact jointly acknowledged bridge payload cleanup is allowed.

All V10 originals remain SOURCE_KEEP. Archived bytes, restoration evidence, bridge cleanup and source disk recovery are separate facts; current source recovery is zero.
