# R5 evidence validation summary

## Isolation

Artifact:
`/data/c16/results/C16_R5_PREFLIGHT_CLEAN_20260914T134529Z/SHA256SUMS.txt`

- Size: `2187` bytes
- SHA256: `bea16257cada1c3013d299ce3764ab2744a7b61ab7d347010ca1efba3aba7eeb`
- Records RTX4080 UUID/driver/runtime, no unrelated compute, no active bulk writer, unchanged transfer/.partial snapshots, and no residual NCU/NVBit/model process.

## U5 repeated native

Artifact:
`/data/c16/results/C16_R5_U5_20260914T135447Z.json`

- Size: `603` bytes
- SHA256: `f6ef1d50c809226149a308a747d62d0780bfe5dd6c2a5b15da413f4e406793e5`
- Model/revision admitted by U4; float16/SDPA/CUDA-only; `tokenizer_invoked=false`.
- Warmup: `806.089855 ms`.
- Five measured durations: `[22.651957, 22.660726, 22.655688, 22.488295, 21.978727] ms`.
- Median/min/max: `22.651957 / 21.978727 / 22.660726 ms`.
- Output checksum: `2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f`.

## U6 target

Launch map:
`/data/c16/results/C16_R5_U6_RETRY_20260914T135752Z/launch.tsv`

- Size: `1880572` bytes
- SHA256: `eba78a615d8cb387de432701277927ccbd836673e0b743b575cefab83f899394`

Static map:
`/data/c16/results/C16_R5_U6_MAP_RETRY_20260914T135827Z/static.tsv`

- Size: `94307` bytes
- SHA256: `c460cebff02ed54516141df705dd012fc541e48a6878e45f88db8c6602c68e25`

Frozen semantic target: `indexSelectLargeIndex`, static index `101`, opcode `LDG.E.U16`. R4 absolute address/launch IDs were not reused.

## U7 NCU

- NCU path: `/opt/nvidia/nsight-compute/2025.1.1/ncu`
- Version: `2025.1.1.0`
- Executable SHA256: `a44ff2c735c4dcf66c78f3f430155805d6a0b1f74f26331f98ecec03bfbf3f1a`
- Metrics recorded: `dram__bytes_read.sum`, `dram__bytes_write.sum`, `smsp__inst_executed.sum`, `sm__cycles_elapsed.avg`
- Reported passes: `1`
- NVBit not co-loaded; clean termination.

Raw report:
`/data/c16/ncu/C16_R5_U7_indexSelectLargeIndex_20260914T135958Z.ncu-rep`

- Size: `21281541` bytes
- SHA256: `22b1ca7096c59e0a5336c963957e4e1b9469becdc857e21bceb5a5ac96658804`

Export:
`/data/c16/results/C16_R5_U7_20260914T135958Z/report.csv`

- Size: `12810` bytes
- SHA256: `c079c278e7fff2689495b3a3965c2ad50e28471cce41e7fe82b7c4da9385fc9e`

The exact R5 U7 argv vector, standalone metric-manifest file/hash and standalone target-contract receipt/hash are not recoverable from currently committed sources and are not reconstructed post hoc.

## U9 NVBit

Fixed target: `indexSelectLargeIndex / 101 / LDG.E.U16`. R5-local U6 launch/static maps are hash-closed above. U8.5 provides READY/no-match lifecycle authority. Target launch was observed; address-bearing rows: `1`; TERMINAL and clean exit were observed; frozen checksum remained stable.

Raw stdout:
`/data/c16/results/C16_R5_U9_20260914T140046Z/raw.txt`

- Size: `2821` bytes
- SHA256: `a47cfe7d298c0519fcb7f78c2737debce1664785fa48cce17e226aff4a03fe5b`

A separate R5 arm/target-binding receipt path+SHA is not recoverable from currently committed sources and is not invented after the fact.

## Classification

- R4: `MECHANISM_QUALIFICATION_PASS / SCIENTIFIC_MEASUREMENT_NOT_ACCEPTED`.
- R5: `R5_SCIENTIFIC_DATA_ACCEPTED_FOR_FROZEN_LLAMA_QUALIFICATION`.
- R6/R6.1: documentation/re-hash only; no scientific workload rerun.
- Repository status: artifact integrity is closed; limited command/receipt replay fields are explicitly documented as non-recoverable.
- Final status: `READY_FOR_MULTIMODEL_REVIEW`.
