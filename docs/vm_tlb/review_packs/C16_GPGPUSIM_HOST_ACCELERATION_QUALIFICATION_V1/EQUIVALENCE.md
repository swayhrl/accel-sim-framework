# Equivalence result

The final 16-kernel real-prefix matrix passed exact comparison for every retained run:

- exact `(UID, stream, kernel name)` sequence;
- exact per-kernel cumulative `gpu_tot_sim_cycle`, `gpu_tot_sim_insn`, and `gpu_tot_issued_cta`;
- exact final `(87146, 613280, 57)` tuple;
- exact termination with exit code 0 and no stderr/assertion;
- exact normalized full stdout SHA `a6ee22685880b90fdd77981dbec162da01035eebd34527a9da79ea2c7793b399`.

Normalization removes only host/build observations: Accel-Sim and GPGPU-Sim build labels, trace container path, `enable_ptx_file_line_stats` echo, host-rate/time/silicon-slowdown lines, and equivalent kernel-file directory prefixes. All cache/interconnect/statistical simulator lines remain in the normalized stream. This is stronger than comparing only the three headline counters.

No `oracle_elastic*` mechanism decision lines are emitted by this non-target prefix. The accepted 59-completion prefix reaches the fill immediately before the first AWQ target, but historical UID168 evidence shows that replay is multi-hour; the attempted exact 59-kernel run was stopped at UID21 after it violated the short-benchmark boundary. Therefore target/victim/protection decision equivalence is `NOT_OBSERVABLE_IN_BOUNDED_PREFIX`, not claimed exact. This blocks qualification independently of the negative speed result.

Allowed observational differences:

- Candidate A removes generic memory-latency, request-latency, ICNT-latency, bank/access and related histogram output.
- Candidate B with config=0 omits the 133-byte header-only `gpgpu_inst_stats.txt` (`bb21a46c51c2cab168764097ace9a99a20b455a56bd49fe2c1eb786966a32a0b8`).
- Candidate C changes only non-authoritative runtime/liveness cadence in this screen.
- Candidate D changes the trace container/path only; payload hashes are exact.

Because the combined candidate is slower, none of these observational changes is admitted into the scientific configuration.
