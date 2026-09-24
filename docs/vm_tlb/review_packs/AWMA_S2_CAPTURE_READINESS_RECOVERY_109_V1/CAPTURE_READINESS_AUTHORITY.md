# Capture readiness authority

- Lane A V2 full per-launch ledger: `hrl/awma-qwen25-s2-census-reclass-v2 @ 24f21db0aa921190ca40e4d3969aced7471347b6`; hash verified as `222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a` with 34,677 rows.
- Driver: `hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`; SHA-256 `824f88b975580288a6a68b6997aa4ce5a611e241c42fd347fc2f59e933faab6c`.
- Input: Qwen/Qwen2.5-0.5B-Instruct revision `7ae557604adf67be50417f59c2c2f167def9a775`, S2 TEXT T2048 SHA-256 `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`.
- Lane C assets use only the documented candidate-index plus exact phase/function/grid/block reconciliation. T0/T1/T2 come from `03924689da9c9691501d93567365c9265178b8a5`; splitkv and splitkv-combine are promoted to reusable by `0fc6c559027b029d79b77c1f6dcfa5162648b1ac`.
- No second legal T2048 TEXT input was recovered. Same-length different-content control remains `INPUT_AUTHORITY_BLOCKED`.
