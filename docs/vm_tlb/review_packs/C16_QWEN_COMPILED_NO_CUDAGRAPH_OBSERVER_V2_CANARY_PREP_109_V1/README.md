# Qwen compiled/no-CUDA-Graph Observer V2 canary: CPU preparation

This pack records CPU-only preparation. The Lane6 contract is not yet present, so GPU execution is blocked. `UPSTREAM_AUTHORITY.json` pins the accepted Mode A/B canary and Observer V2 source. `STATIC_QUALIFICATION.json` proves exact semantic AST extraction, zero per-occurrence CUDA Events, balanced NVTX, ordinal and shape receipts. `ASSET_INPUT_PREP.json` rechecks the fixed Qwen model and inputs. `TESTS.json` records compilation and directed synthetic gates. `CONTRACT_POLL.tsv` records five-minute Lane6 checks.

No CUDA initialization, model load, GPU lock, observer run, NSYS, NCU, Tier0, or holdout occurred in this preparation.
