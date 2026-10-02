# START HERE — AWMA R25 tied-weight broader software validation

Date: 2026-10-02

Stage:
`AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1`

Execution branch to create on node109:
`hrl/awma-r25-tied-weight-broader-validation-109-v1`

Handoff branch:
`hrl/awma-r25-tied-weight-broader-validation-handoff-v1`

Scientific parent / current-state authority:
`b73ffd2320b5ee952d90625089b2ec31eb25eab4`

R24 execution:
`41795817a5b86959c86cc36c6973f292be33c6a6`

R24 is COMPLETE/STOP. Its empirical result is:
- large causal peak-memory reduction from the tiled delayed-update path;
- S2 stably faster than S1;
- S2 vs B0 mixed/near-neutral;
- no hardware claim.

This R25 Goal does **not** tune or extend the R24 discovery point. It tests:
1. a stronger one-full-buffer software comparator; and
2. one independent model/input performance holdout.

No node174/Accel-Sim or hardware/PPA work is authorized.

## Two validation points

### D0 — discovery/calibration point
Exact R24 Qwen2.5-0.5B real-token point:
- Qwen/Qwen2.5-0.5B-Instruct
- revision `7ae557604adf67be50417f59c2c2f167def9a775`
- accepted `ACCEPTED_R101_TRAIN_DISCOVERY_256` token authority
- B=1, T=255, H=896, V=151936.

### H0 — independent performance holdout
Existing accepted C16 asset:
- `meta-llama/Llama-3.2-1B`
- revision `4e20de362430cd3b72f300e6b0f18e50e7166e08`
- expected source receipt:
  `/data/c16/models/.provenance/R1_LLAMA3P2_1B_ASSET_RECEIPT.json`
- expected source-receipt SHA256:
  `7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47`
- use the already accepted frozen `S0/B1/T128/Decode4/TEXT` token binding.
- do **not** retokenize or download a new model/input.
- for this training microstep, take the frozen T128 token IDs and use
  `input_ids=tokens[:-1]`, `labels=tokens[1:]`.

The exact H0 bundle path, binding receipt and token-ID hashes must be resolved
from accepted C16 authority before any GPU performance work. If a unique accepted
bundle cannot be resolved, STOP; do not substitute another input.

## Arms

- `B0_DENSE_STRONG`: R24-style strong dense baseline.
- `C1_COMPACT_FULL`: compact lookup-side rows + one full classifier/total gradient.
- `S2_TILED`: compact lookup-side rows + bounded tiled classifier gradient/update,
  never a formal full VxH gradient.

Primary comparison:
`S2_TILED vs C1_COMPACT_FULL`.

B0 is retained as a historical/causal anchor, not the only production comparator.

Read and execute:
`docs/vm_tlb/chatgpt_handoff/awma/r25_tied_weight_broader_validation_v1/LANE_G_R25_TIED_WEIGHT_BROADER_VALIDATION_109_GOAL.md`

All CUDA/JIT activity holds:
`/data/c16/locks/c16_gpu_campaign.lock`

Node164 remains durable authority. Node109 may use active replicas. Node174 is not involved.
