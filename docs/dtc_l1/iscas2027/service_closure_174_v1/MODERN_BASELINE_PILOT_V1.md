# Contemporary baseline-only pilot V1

Predeclared cohort: BICG, Btree, 2DConvolution, Hotspot1, complete frozen ordered trace lists and instruction scopes. No shortened replacement, winner selection, native speedup claim, or cohort average is permitted.

Use the unmodified RTX4080 config bytes from Framework `8d1f14a32f5538660d74da86ccb03a2c504c5735`, copied to `config/RTX4080_FROZEN_BASELINE.config`. A separate scope overlay explicitly selects LEGACY mode 0. The canonical source is `6582b9d171330d88b17e8d5294c97704229e3823`, existing binary SHA256 `4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9`. This source has no AWMA translation code and mode 0 does not execute PAPER_BASE PIB=8 or MSHR=32 overrides. The conventional L1 starts with MSHR=384/merge48 and the frozen sector tuple. The asset's adaptive sizing and write ratio25 remain part of this diagnostic identity.

This is an **old-SASS modern-memory-parameter model counterfactual**. Preserve the frozen FAST64 trace-execution config (`19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e`) including Volta-era trace opcode timings. These are not Ada native instruction timing measurements or a qualified modern native binary. The split is deliberate and explicit: isolate memory-parameter relevance using identical old instruction streams, then consume a separate immutable 109 native receipt if supplied. Do not silently substitute native qualification or make RTX4080 performance predictions from this diagnostic.

Before acceptance, verify the executed mode, effective MSHR, per-kernel L1 sizes/allocation policy, kernel completion, complete instructions, L1-exposed load paths, and L2/DRAM activity. The generic attempt validator establishes only terminal identity/instruction checks; it is not full scientific acceptance. Retain all nonzero exits. A parser/config/provenance repair may resume on a new immutable UUID; an instruction-domain or scientific-identity change needs review.

Run at most four small workers; do not replay closed SG3 or old whole matrices. Raw immutable attempts stay outside Git under `/workspace/dtc-service-closure-174-v1/modern-baseline-attempts`. Compatible baselines may be shared by later comparisons after row equivalence is established. Modern DTC additionally remains HOLD under the fixed128KiB capacity/service review; passing R1 alone does not release that gate.

All four baseline-only rows completed and passed independent terminal, complete-instruction/kernel, source/config, mode0, adaptive-size and actual cache/DRAM-path checks. Exact UUIDs, hashes and metrics: `review_pack/checkpoint_20261016T0918Z/MODERN_BASELINE_ONLY.tsv`.

Subsequent complete body auditing discovered the [Hotspot shared-address interpretation boundary](HOTSPOT_SHARED_FORMAT_REVIEW_V1.md). Its original consumer-model number remains preserved, while semantic comparison promotion is HOLD. New checkpoint tables explicitly carry that annotation. The terminal/invariant PASS does not resolve the historical encoder contract.

| Workload | Complete instructions | Cycles | Effective L1 KiB per kernel | L2 misses | DRAM read commands |
|---|---:|---:|---|---:|---:|
| BICG |145666048|2091175|128,128|41984|41472|
| Btree |444467849|126797|128,128|0|0|
| 2DConvolution |620347492|609625|128|4061696|1965568|
| Hotspot1 |377291004|67494|96|137224|6152|

The frozen `gpgpu_perf_sim_memcpy=1` fills L2 from recorded HtoD commands (`gpu-simulator/accel-sim.cc::parse_commandlist`, Core `gpu-sim.cc::perf_memcpy_to_gpu`). Thus Btree's zero DRAM commands describe this input/initialization/cache regime, not absence of L1 traffic or a general native result. All four execute global reads through L1. L1T/L1C recorded accesses are zero for this pilot; those auxiliary paths are not expanded by a DTC claim.

DRAM command counts sum each of eight controllers' last cumulative `n_rd+n_rd_L2_A` and `n_write` fields. The separate `total dram reads/writes` bank-stat field prints zero even with executed reads and is not used. The configured bus4×burst16 represents64B per command; L2/cache misses and DRAM commands are different units and are not equated. The unused `n_ref_event` field is not a measurement here. All these limits remain part of the memory-parameter counterfactual identity.
