# AWMA R102 real update boundary 109 V2

Final decision: `R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2`.

Start with `FINAL_DECISION.md`, then `AUTHORITY_SEARCH.md`, `SOURCE_INPUT_RECEIPT.json`, and `VERSION_CHAIN.tsv`.

The bounded Round16 search found a real public TRL AsyncGRPO anchor/delta bucket, but it does not satisfy the frozen Form-B contract: patch headers have no base hash or reconstructed-target hash, and the public consumer applies patches without wrong-base rejection or target-hash verification. PULSE exposes no separate public chain; GRAIL exposes code but real R2 checkpoints require credentials and no GitHub release contains checkpoint assets. No new local/node164 chain appeared after the historical R102 audit.

Input admission therefore stops before bucket freeze. `BUCKET_MANIFEST.tsv`, `CHANGE_DISTRIBUTION.tsv`, `CORRECTNESS_TESTS.tsv`, and `BREAK_EVEN_ANALYSIS.tsv` explicitly record `NOT_RUN_INPUT_AUTHORITY_FAILED`. B0/B1/B2/D1 timing and profiling files are absent by design. CUDA operations: 0. GPU-lock acquisitions: 0.
