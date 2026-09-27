# R54 V1R2 greedy backend decision

State: `R54_V1R2_GREEDY_BACKEND_QUALIFIED`.

All three frozen prefixes (64, 2048, 4096 tokens) produced identical 64-token greedy IDs in clean fallback and Hub processes. EOS/stop position, length, cache progression and finite logits passed. Across 192 diagnostic steps, top2 order differed at 7 steps; those values remain in `R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv`. No numerical tolerance was introduced.

V1 and V1R1 remain as separate accepted negative results. The Hub backend was eligible for the checkpoint lifecycle under this application contract.
