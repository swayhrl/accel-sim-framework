# R5 U7 NCU provenance

## Tool identity

- Executable: `/opt/nvidia/nsight-compute/2025.1.1/ncu`
- Version: `2025.1.1.0`
- Executable SHA256: `a44ff2c735c4dcf66c78f3f430155805d6a0b1f74f26331f98ecec03bfbf3f1a`
- Tool identity source: reviewed NCU N0 authority at `ba9afb264746b3290607ae5e5e5d8642941bc11f`.

## Capture identity

- Frozen semantic target: `indexSelectLargeIndex`.
- Frozen static instruction: index `101`, opcode `LDG.E.U16`.
- Metrics recorded by the R5 evidence: `dram__bytes_read.sum`, `dram__bytes_write.sum`, `smsp__inst_executed.sum`, `sm__cycles_elapsed.avg`.
- Reported pass count: `1`.
- NVBit was not co-loaded; termination was clean.

Raw report:
`/data/c16/ncu/C16_R5_U7_indexSelectLargeIndex_20260914T135958Z.ncu-rep`

- Size: `21281541` bytes
- SHA256: `22b1ca7096c59e0a5336c963957e4e1b9469becdc857e21bceb5a5ac96658804`

CSV export:
`/data/c16/results/C16_R5_U7_20260914T135958Z/report.csv`

- Size: `12810` bytes
- SHA256: `c079c278e7fff2689495b3a3965c2ad50e28471cce41e7fe82b7c4da9385fc9e`

## Repository replayability boundary

The currently committed R5/R6.1 evidence does **not** preserve a byte-for-byte exact U7 argv vector, a standalone metric-manifest file/hash, or a standalone R5 target-contract receipt/hash. These fields are therefore `NOT_REPOSITORY_RECOVERABLE` from the present committed sources and are not reconstructed post hoc.

This is a documentation/replay-transcript limitation, not an artifact-integrity failure: the tool identity, frozen semantic/static target, raw report and exported report are independently hash-closed and were re-hashed successfully during R6/R6.1.
