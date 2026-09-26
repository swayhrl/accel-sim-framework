# START HERE — AWMA R54 Long-Horizon V1

Node:
109 / RTX4080 / SM89

Branch:
`hrl/awma-r54-long-horizon-handoff-v1`

Read in order:

1. `docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_LONG_HORIZON_HANDOFF_CONTEXT_2026-09-27.md`
2. `docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_MEASUREMENT_CONTRACT_V1.md`
3. `docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/CODEX_GOAL_109_R54_LONG_HORIZON_V1.md`
4. literature:
   `hrl/awma-chatgpt-literature-notes-v1 @ 85ddfac657e6bf2ae99ddd0997d4311f210f341c`
   `docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_07_R54_LONG_HORIZON_SELECTION.md`

Primary stage:
`AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

Continuous execution chain:

`source/runtime -> model -> fixture -> exact state schema -> P0/P1/P2 correctness -> production timing -> restore semantics/timing -> amortization -> conditional holdout/NCU -> R55 source audit -> node164/Git closure`

Important:
- one Qwen3.5-0.8B model only;
- no node174;
- no Accel-Sim;
- no hardware mechanism;
- no checkpoint-density sweep beyond D512/D2048;
- no R55 GPU benchmark;
- negative/not-qualified outcome is valid;
- ordinary engineering problems solve-and-continue;
- STOP once a coherent final scientific state and publication closure are complete, even if the human's unattended window is not exhausted.

No auto merge.
