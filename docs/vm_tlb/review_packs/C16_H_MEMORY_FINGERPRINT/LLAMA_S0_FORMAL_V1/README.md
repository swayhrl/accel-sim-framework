# C16 H Llama S0 formal memory fingerprint V1

Status: `FORMAL_ADMITTED` for six SHA-closed Recovery-V2 raw traces.  This
pack is distinct from, and does not revise, `../LLAMA_S0_V1/`, whose historical
M4A inputs remain exploratory only.

The formal selected targets are a single `indexSelectLargeIndex` instruction
for Prefill and a single `indexSelectSmallIndex` instruction for Decode.  This
is not a whole-model memory, TLB, cache, or page-table characterization.
Observed addresses are `GPU_VA_OBSERVED`, and all overlap measurements are
`SET_ONLY`; neither physical-address nor global-L2 temporal claims are made.

`S5` supplies the principal Prefill and Decode2/3/4 results. `S3` and `S4`
are independent-process Prefill reproducibility checks.  Absolute VA sets are
not compared across independent processes or across Prefill and Decode.
