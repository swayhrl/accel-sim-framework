# C16 RTX4080 U5-U9 R4 execution report

Status: `READY_FOR_NEXT_STAGE`.

- U5: PASS — frozen 128 IDs, float16/sdpa, CUDA-only Llama native baseline; output checksum `2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f` matches historical authority.
- U6: PASS — RTX4080 live NVBit launch inventory recorded actual `indexSelectLargeIndex` mangled function and address; no RTX3090 target was reused.
- U7: PASS — NCU 2025.1.1 profiled RTX4080 canonical `indexSelectLargeIndex`, one pass, raw `/data/c16/ncu/C16_U7_Llama_indexSelectLargeIndex_20260914T130914Z.ncu-rep`.
- U8.5: reviewed PASS.
- U9: PASS — actual static map, static index 101 `LDG.E.U16`, target launch, nonzero address record, complete terminal, stable output checksum.

Raw U9 stdout: `/data/c16/results/C16_U9_TARGET_20260914T131459Z/raw_target_stdout.txt`, SHA256 `5b2b5386a8d72130413a711e5b95558891ef7b7c4dcfe2068c59c87842de5292`.

Review entry: `docs/vm_tlb/review_packs/C16_4080_U5_U9_R4/README.md`.
