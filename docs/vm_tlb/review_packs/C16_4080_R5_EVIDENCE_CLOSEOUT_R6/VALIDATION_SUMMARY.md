# R5 isolation

{
  "path": "/data/c16/results/C16_R5_PREFLIGHT_CLEAN_20260914T134529Z/SHA256SUMS.txt",
  "size_bytes": 2187,
  "sha256": "bea16257cada1c3013d299ce3764ab2744a7b61ab7d347010ca1efba3aba7eeb"
}
Preflight records RTX4080 UUID/driver/runtime, no unrelated compute, no active bulk writer, unchanged transfer/.partial snapshots, and no residual NCU/NVBit/model process.

# R5 U5 repeated native

{
  "path": "/data/c16/results/C16_R5_U5_20260914T135447Z.json",
  "size_bytes": 603,
  "sha256": "f6ef1d50c809226149a308a747d62d0780bfe5dd6c2a5b15da413f4e406793e5"
}
Model/revision admitted by U4; float16/SDPA/CUDA-only; tokenizer_invoked=false. Warmup 806.089855 ms; durations [22.651957, 22.660726, 22.655688, 22.488295, 21.978727]; median/min/max 22.651957/21.978727/22.660726 ms; checksum 2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f.

# R5 U6 target

Launch map: {"path": "/data/c16/results/C16_R5_U6_RETRY_20260914T135752Z/launch.tsv", "size_bytes": 1880572, "sha256": "eba78a615d8cb387de432701277927ccbd836673e0b743b575cefab83f899394"}
Static map: {"path": "/data/c16/results/C16_R5_U6_MAP_RETRY_20260914T135827Z/static.tsv", "size_bytes": 94307, "sha256": "c460cebff02ed54516141df705dd012fc541e48a6878e45f88db8c6602c68e25"}
Frozen semantic target indexSelectLargeIndex, static index 101, opcode LDG.E.U16. R4 absolute address/launch IDs were not reused.

# R5 U7 NCU

NCU /opt/nvidia/nsight-compute/2025.1.1/ncu version 2025.1.1.0; metrics dram__bytes_read.sum, dram__bytes_write.sum, smsp__inst_executed.sum, sm__cycles_elapsed.avg; one pass; NVBit not co-loaded; clean termination.
Raw: {"path": "/data/c16/ncu/C16_R5_U7_indexSelectLargeIndex_20260914T135958Z.ncu-rep", "size_bytes": 21281541, "sha256": "22b1ca7096c59e0a5336c963957e4e1b9469becdc857e21bceb5a5ac96658804"}
Export: {"path": "/data/c16/results/C16_R5_U7_20260914T135958Z/report.csv", "size_bytes": 12810, "sha256": "c079c278e7fff2689495b3a3965c2ad50e28471cce41e7fe82b7c4da9385fc9e"}

# R5 U9 NVBit

Fixed target indexSelectLargeIndex/101/LDG.E.U16; R5-local map/arm binding; READY/no-match lifecycle authority U8.5; target launch observed; one address-bearing row; TERMINAL and clean exit; frozen checksum 2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f.
Raw stdout: {"path": "/data/c16/results/C16_R5_U9_20260914T140046Z/raw.txt", "size_bytes": 2821, "sha256": "a47cfe7d298c0519fcb7f78c2737debce1664785fa48cce17e226aff4a03fe5b"}
