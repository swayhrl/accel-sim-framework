# GEMM counter interpretation correction — additive evidence V1

Correct the interpretation of `SCIENCE_INCREMENT_293_V5` (commit `fbb372be0301966fa556fc9ec5f2e6e1dfa40662`): **GEMM DRAM percentage null is caused by a zero denominator, not missing DRAM read counts**. Original data and report remain untouched; this addendum supersedes only the erroneous missing-counter interpretation.

All eight DH variants E384/E768/M8/M16/Q64/Q128/F128/F256 have exactly826,089 cycles, same as DH P0, hence1.0x. Their V5 counters explicitly contain DRAM read atoms0→0, delta0; derived bytes0→0. The percentage is undefined because P0=0. L2 accepted global reads are1,716,504→1,716,504, all hits; L2 read misses/sectors and reservation failures are0. `avg_mrq_latency_last_printed=None` remains genuinely absent/unprinted, and must not be turned into zero.

Only GEMM DH P0 and E384 raw logs were reopened, with compressed/uncompressed SHA and strict/result closure checked. All20 controller `n_req`, `n_rd` and `n_write` values in these raw statistics are explicit0. P0 final L2 breakdown lines3399–3404 show HIT1,716,504 and MISS/SECTOR_MISS0; totals at3490 confirm read count. E384 matches. All eight immutable RESULT SHAs were revalidated; the other six raws were not rescanned.

The unchanged configuration and trace explain the observed insensitivity: `-gpgpu_perf_sim_memcpy=1`, perfect_mem=0, L2flush=0. The command list contains three1MiB HtoD copies before `_Z11gemm_kernelPfS_S_`, grid16x64, block32x8, one kernel. Framework `accel-sim.cc:139` calls `perf_memcpy_to_gpu`; Core `gpu-sim.cc:2670–2694` sends copies to `l2cache.cc:109–119`, which directly forces L2 tag updates. These3MiB fit within fixed10MiB L2. The available PolyBench source snapshot defines NI/NJ/NK512 and maps the matching kernel/index pattern; this is source mapping evidence, not a new certification of the historical capture binary/build. Observed all-hit/no-DRAM-kernel statistics are consistent with this memcpy-preloaded L2 path, so changing L2 miss-side resources has no exercised read-miss path here.

Do **not** generalize this to a real GEMM application's total DRAM traffic, a cold-cache execution, host copy cost, or another input. This model's memcpy handling fills L2 without timing those copies as ordinary DRAM requests. The analysis is confined to this accepted declared trace/kernel and its printed statistics; historical capture-completeness status is unchanged. `gpu_stall_dramfull=1,165,837` does not contradict the zero DRAM requests: `gpu-sim.cc:1866` prints `gpu_stall_icnt2mem` under that legacy label, and2467 increments it when an ICNT packet waits on a full memory subpartition, not as a direct DRAM queue-latency measure.

GEMM and sgemm are different frozen identities:

| Program | Suite | Input digest | Declared population |
|---|---|---|---|
| GEMM | PolyBench/GPU |fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318|1024 CTA,739,246,080 instructions,1 kernel|
| sgemm | Parboil |ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453|528 CTA,1,658,916,864 instructions,1 kernel|

All paths, SHAs, exact source excerpts, config subset, trace command list and per-profile numbers are in `EVIDENCE.json`. No simulation, production edit, counter imputation, old-result replacement or input promotion occurred.
