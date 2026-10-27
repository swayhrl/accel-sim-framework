DTC L2 MLP parameter contract V1

Core 9eedb3131937748f0492fa83aad37d3691118d70; Framework 02775fd795cde5aae1480d81cee6eb481d0a08f4. Both tracked trees clean. Binary and library SHA independently re-read.
Fixed effective L2: S:128:128:16,L:B:m:L:L,A:192:4,32:0,32. 40 subpartitions, 256KiB each, total10MiB. DRAM850MHz; core/ICNT/L2 clocks1410MHz.

|Profile|Entries/bank|Request-list max/key|Miss queue/bank|FRFCFS/controller|Total MSHR keys|Total request-reference bound|Shared credits/controller|
|---|---:|---:|---:|---:|---:|---:|---:|
|P0|192|4|32|64|7680|30720|255|
|E384|384|4|32|64|15360|61440|255|
|E768|768|4|32|64|30720|122880|255|
|M8|192|8|32|64|7680|61440|255|
|M16|192|16|32|64|7680|122880|255|
|Q64|192|4|64|64|7680|30720|255|
|Q128|192|4|128|64|7680|30720|255|
|F128|192|4|32|128|7680|30720|319|
|F256|192|4|32|256|7680|30720|447|

Interpretation and boundaries

MSHR merge includes the first request. Sector cache MSHR keys use32-byte atom alignment; a key count is not a cache-line count.
FRFCFS is a coupled factor: shared credits=F+192−(2−1)=F+191; private credit limit remains1/subpartition. F64/128/256 gives255/319/447 shared credits/controller. Partition FIFOs remain64:64:64:64.
Miss queue values are configured bounds. Admission paths differ (<size versus size+num_miss>=bound), so do not assert every operation may occupy exactly the configured count.
Logical capacities do not establish physical area, queue latency, dynamic power, or fully allocated host RSS. Cache data capacity is fixed10MiB. High-resource profiles require explicit overhead disclosure.

CPU qualification

PASS: 142 mutation/invariant checks; 44 isolated actual-Core option-parser cases; no simulator launches or model cycles.
The fixture links only src/option_parser.cc. It uses the exact cache sscanf format/order plus fixed-geometry assertions; it does not instantiate a complete cache or simulator. Initial fixture token-count assertion was corrected from16 to15 before finalPASS; no scientific run identity was consumed.
CH and DH P0 remain byte-identical. All variants differ only at the final effective L2/FRFCFS option. Old shadow definitions are retained. Every non-target effective option is compared.

Integration

Use l2_config_generator.generate(texts, "E384") or generate(texts, {"entries":384,"merge":8}). Returns ordered config texts plus exact effective options, SHA, changes and slot costs. Only coordinator registers and dispatches.
Templates support all eight one-factor profiles, nine evidence-gated combinations, and finite resource-qualified expansion (next examples E1536/M32/Q256/F512). These bounds are not stopping criteria or a launch budget.
Avoid zero/unlimited windows. Do not modify finite service, DTC-L1, mapping, capacity, clocks or inputs. Same cell/input/build P0 proof is required for reuse.

Precise source evidence

- cache_parser: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:578–586, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- cache_guards: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:715–760, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- mshr_atom_address: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:833–834, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- mshr_construction: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:1044–1058, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- kernel_parameter_invariance: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:1080–1087, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- merge_capacity_semantics: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.cc:581–595, SHA256 f600601f96c07b6618f198e7b37dd394f07bb286a5d7b7f76c72634d7f2b1dd1
- miss_queue_admission: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-cache.h:1493–1495, SHA256 092946c8149946f37d381ad86eff8b4df31ece9e7dd52cb0fbe3836aa900c1c9
- option_registration_L2: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-sim.cc:260–264, SHA256 8e159a05a385e2d29799363d5786dcabff6aff770675b8b4221864e6c4f0355c
- option_registration_FRFCFS: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-sim.cc:293–298, SHA256 8e159a05a385e2d29799363d5786dcabff6aff770675b8b4221864e6c4f0355c
- separate_write_default: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/gpu-sim.cc:331–336, SHA256 8e159a05a385e2d29799363d5786dcabff6aff770675b8b4221864e6c4f0355c
- FRFCFS_admission: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/dram_sched.cc:72–88, SHA256 2a0280247c5558541dc3896f86bc596549dd83b71630717cc40756248fee3e73
- credit_coupling: /root/data/dtc_failure_repair_20261025_v1/core/src/gpgpu-sim/l2cache.cc:130–149, SHA256 1b2b0ebca49a2f5943c9350a637d849961da96159a147a70b887434bd7f37ff5
