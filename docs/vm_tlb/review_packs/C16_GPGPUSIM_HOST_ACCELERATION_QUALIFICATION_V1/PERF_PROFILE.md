# Phase 0 host profile

`perf` was unavailable (`perf: command not found`) and `/proc/sys/kernel/perf_event_paranoid` was `4`; no kernel security setting was changed. No ptrace/gdb sampling was used because it would stop the target. The permitted low-intrusion fallback sampled `/proc/<pid>/{schedstat,sched,status,io,stat}` for 30 seconds while the three existing simulators continued unmodified.

All three simulators were single-threaded, remained on their pre-existing pinned CPUs, had zero migrations, zero new major/minor faults, and zero block-I/O bytes. CPU runtime fractions were 99.80% (R0), 99.72% (M1), and 99.84% (diagnostic); runqueue-wait fractions were 0.32%, 0.40%, and 0.27%. The workload is compute-bound with trace data served through page cache/decompression, not block-I/O bound.

Hardware IPC/cache-miss/branch-miss counters are `UNAVAILABLE_ENVIRONMENT`, not silently inferred. The empirical configuration screens and source-path inspection therefore provide the hotspot ranking:

1. PTX/source-line map updates: source-confirmed unconditional map paths when config=0; candidate guards were exact but showed -1.49% over five final repetitions.
2. Generic memory latency/bank counters: source-confirmed hot-path updates, but `memlatency_stat=0` measured -0.59%.
3. Periodic/runtime output: `runtime_stat 10000:0` measured +1.72%; below material threshold. Current flag bits are zero, so no large runtime-stat body executes.
   The retained stdout is about 890 KB for 16 kernels (~55.6 KB/kernel); required final and cache statistics were not removed.
4. Trace input/decompression: predecompressed +0.36%; byte-exact tmpfs compressed staging -0.45%; block reads were zero during live sampling.
5. CPU placement: all-CPU median was 1.11% faster than CPU300 on the short prefix; pinned distinct physical cores remain useful for isolation, not a claimed speedup.
6. Compiler: release is already `-O3`; LTO/PGO were considered but not promoted after all lower-risk candidates failed the material-gain gate. `-ffast-math` was never used.

The raw sample is `raw/live_primary_proc_20260927T0250Z.txt` (SHA-256 `91464cc23d4f109b02febf59c94052f3537dd6189504e126fbef50c3a43c058c`).
