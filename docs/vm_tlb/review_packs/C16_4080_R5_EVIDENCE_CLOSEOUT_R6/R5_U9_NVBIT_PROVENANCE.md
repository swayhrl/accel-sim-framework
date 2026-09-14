# R5 U9 NVBit provenance

## Frozen target and lifecycle

- Frozen semantic target: `indexSelectLargeIndex`.
- Frozen static instruction: index `101`, opcode `LDG.E.U16`.
- U6 R5-local launch map: `/data/c16/results/C16_R5_U6_RETRY_20260914T135752Z/launch.tsv`
  - Size: `1880572` bytes
  - SHA256: `eba78a615d8cb387de432701277927ccbd836673e0b743b575cefab83f899394`
- U6 R5-local static map: `/data/c16/results/C16_R5_U6_MAP_RETRY_20260914T135827Z/static.tsv`
  - Size: `94307` bytes
  - SHA256: `c460cebff02ed54516141df705dd012fc541e48a6878e45f88db8c6602c68e25`
- READY/no-match lifecycle authority: reviewed U8.5 closure.
- Target launch observed: yes.
- Address-bearing rows observed: `1`.
- TERMINAL / clean exit: yes.
- Frozen model checksum: `2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f`.

Raw stdout:
`/data/c16/results/C16_R5_U9_20260914T140046Z/raw.txt`

- Size: `2821` bytes
- SHA256: `a47cfe7d298c0519fcb7f78c2737debce1664785fa48cce17e226aff4a03fe5b`

## Repository replayability boundary

The committed R5/R6.1 evidence confirms an R5-local map/arm binding but does **not** preserve a separate arm/target-binding receipt path+SHA that can be independently recovered from Git alone. That field is therefore `NOT_REPOSITORY_RECOVERABLE` from the present committed sources and is not invented after the fact.

The U9 scientific qualification remains structurally closed for the fixed canary because the R5-local launch/static maps, frozen semantic/static target, successful target launch, nonzero address row, stable checksum, TERMINAL state, and raw stdout hash are all recorded. This canary is not a whole-model Llama memory-behavior claim.
