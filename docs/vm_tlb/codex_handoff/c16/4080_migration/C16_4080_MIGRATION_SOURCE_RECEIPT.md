# C16 RTX4080 migration source receipt

## Frozen scope

This CPU-only receipt freezes the source closure from `hrl/vm-c16-g-retry570-v0` at `a58d4479842f4b259cfbf3799ed9327d39cde2c7`. No GPU process was started and no Recovery-V3 scientific asset was changed. The machine-readable authority is [C16_4080_MIGRATION_SOURCE_RECEIPT.json](C16_4080_MIGRATION_SOURCE_RECEIPT.json).

The final hash-closed successful model-level NVBit evidence in this branch is Llama Recovery-V2 S5: `S5_FULL_WORKLOAD_CAPTURE_PASS`, `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`, `S0/B1/T128/Decode4/TEXT`. Its publication manifest is `0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc` and raw index is `e212bf105a4a3e2dba0c3cbddbcb7b7a8812eee8cfd3d6612314b52489baf426`.

Recovery-V3 does not supersede this success: its later R5 outcomes are `PREDICATED_OFF_TARGET` (Qwen0) and `QWEN7_RAW_S1_PREFILL_DIRECT_MEMORY_CAPABILITY_LIMITED_TWO_EXACT_TARGETS_ZERO`. They are retained as negative controls, not successful capture evidence.

## Closure

| Class | Pinned value |
| --- | --- |
| KNOWN_GOOD_REQUIRED | NVBit 1.7.5; archive `e2290da5e35a43fc4c74917dd08e1d41ece3e21bfca6fd7c6dc590c9c8385328`; `core/libnvbit.a` `562348c32b88bf3e5b32d1895202893adb79f32b896e3cac56b29a306de40a12`; `CUDA_MODULE_LOADING=EAGER` |
| KNOWN_GOOD_REQUIRED | C16 tracer source `ac4f678a815954e4ddb22c15d9a8d3841fca86a3`, source SHA `414bdeebebf807a1134a53079ed0b7eee47e7fb3eda72250da25b445f5876ab4`, binary SHA `9e059b6a5b17a74e597169e365ad05d1e82517decad9974868b2b8a195132ae5` |
| KNOWN_GOOD_REQUIRED | Driver `570.124.04`; CUDA/nvcc `12.4` / `12.4.131`; nvdisasm `12.4.127`; CPython `3.10.12` source SHA `a43cd383f3999a6f4a7db2062b2fc9594fefa73e175b3aedafa295a51a7bb65c` |
| KNOWN_GOOD_REQUIRED | torch `2.5.1+cu124`; `libtorch_cuda.so` `761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`; transformers `4.46.3`; AutoAWQ `0.2.7.post3` |
| KNOWN_GOOD_REQUIRED | 66-wheel manifest SHA `ebae0934de68b36e08da5db0e6bfdc47880620205e8bf6d8c8afe8906abc2d2d`; requirements SHA `8085caecebf1e641cb6ab1f2c0e2d8e8cfd5007fd8236b6c10771b223052fa82` |
| KNOWN_GOOD_RECOMMENDED | A single RTX4080 UUID bound to logical `cuda:0`, recorded before the canary. The historical receipt does not record `CUDA_VISIBLE_DEVICES`; preserve the policy, not an invented ordinal. |
| UNKNOWN | Historical 1.7.5 NVBit extraction/build argv, C16 tracer build argv, CPython configure/make/install argv, and final-model `LD_LIBRARY_PATH`. Do not invent them. |

The model runtime bridge is phase-specific: Prefill `1819b0a0062be6fe97f1207d94cd1bc91545e107` / `retry570_multimodel_capture.py` blob `968a658d6e70b128183ac369161d3e81feb46318`; Decode `78234a4bf155c2002bb61486081b49b964b86b4e` / the same file blob `0fc731ee6387880b1ebf0bc27480373a0565298d`. Publication producer is `01d688227d828468421d6eb4d12f89808206027c` (blob `88f80ef80a1ed43ffa33dc8cb1f39b0c04cfce03`).

The source defines a diagnostic targeted-tool command, but it is not historical S5 build evidence:

```bash
make -f util/vm_tlb/c16/lane_g/Makefile.retry570_targeted_memory_tool \
  NVBIT_HOME=<verified-release-root> NVCC=/usr/local/cuda-12.4/bin/nvcc \
  ARCH=sm_86 OUT=<fresh-tool.so>
```

## Environment and prewarm gate

Set `CUDA_MODULE_LOADING=EAGER` before process creation. A child PATH must place `/usr/local/cuda-12.4/bin` before inherited PATH. The injection contract is `CUDA_INJECTION64_PATH=<verified tracer>`, `C16_NVBIT_LD_PRELOAD_DECLARATION=<same tracer>`, `USER_DEFINED_FOLDERS=1`, fresh `TRACES_FOLDER`, `TOOL_COMPRESS=0`, `TRACE_FILE_COMPRESS=0`, and `ACTIVE_FROM_START=0` for the formal model ROI. `DYNAMIC_KERNEL_RANGE` must be rebuilt from an exact 4080 map; it is never copied from the RTX3090 binary.

The bounded order is mandatory: verify identity/hashes → EAGER process → no-capture prewarm outside `MEASUREMENT_ACTIVE` → checksum plus zero-trace/no-match proof → normal exit and no child/GPU process → emit `READY` → parent acquires lease and creates `MEASUREMENT_ACTIVE` → verify no pre-arm trace → write immutable arm → one bounded capture. On failure use process-group `SIGTERM`, two-second grace, then `SIGKILL` only if needed; retain the failed directory and do not reuse it.

## Raw closure

S5 holds six raw traces totaling `16,319,706` bytes: three 5,397,471-byte Prefill traces and Decode2/3/4 traces of 42,431 bytes. Every payload was remote SHA/size recorded, copied to a distinct local path, locally rehashed, and required to match; payloads remain outside Git. Do not remove a remote tree until its local counterpart and closure receipt validate and `remote_only_required_artifact_count=0`.

The raw source is `/root/autodl-tmp/c16_retry570/raw/recovery_v2`; the local layout is `artifacts/c16_g_retry570/recovery_v2/<run>/remote_payload/traces`. All six SHA256 values and their stages are in the JSON receipt.

## Negative controls

- SUPERSEDED — NVBit 1.7.6: `instr_count_bb` and memory trace timed out before workload kernels on elementwise/GEMM.
- DIAGNOSTIC_ONLY — NVBit 1.8: simple elementwise/GEMM tools passed, but exact EMPTY first-use later hung before READY within 60 seconds; not a model-capture substitute.
- SUPERSEDED — LAZY: requested 1.7.5 LAZY was observed by the vendor core as EAGER; model protocol requires EAGER.
- DIAGNOSTIC_ONLY — `instr_count` versus `instr_count_bb`: tool-granularity evidence only, never model-capture equivalence.
- DIAGNOSTIC_ONLY — Retry571/Retry585: `UNKNOWN`; no hash-closed authority-branch receipt was located, so neither can override this closure.

The primary input files are hash recorded in JSON: the known-good runtime profile, S5 summary, S5 raw index, engineering-unblock receipt, and 66-wheel manifest.
