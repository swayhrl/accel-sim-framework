# Semantic trajectory schema

The canonical comparison projects each request event onto: request ID, logical step, block/subblock, cohort ID, request-finished transition, frozen cohort full-refresh/reuse decision, cache epoch/action, committed positions/token IDs, forced-commit positions, stop transition, and next-block seed. Final token and rendered-text hashes are additional gates. Execution-only `REUSE_PACKED` normalizes to semantic `REUSE`; input rows, packing bytes and buckets remain work ledger fields, not algorithm state.
