# Window C — concurrent focused compile/runtime canary while A C3 runs

Goal: `C10B0_CONCURRENT_FOCUSED_COMPILE_CANARY`

Status: `PREPARED / ONLY_WITH_FRESH_A_CONCURRENT_GATE / NO_FULL_BUILD`.

This is a bounded pre-terminal canary. It does not replace the post-terminal C10-B workflow and does not authorize C5.

## Authoritative inputs

Framework:
- branch `hrl/vm-m4b-speculative-v0`
- C10-A2 evidence HEAD `447ad52cf867e35a616fa16ab12e32b8914f50b9`

Core:
- branch `hrl/vm-m4b-speculative-v0`
- C10-A2 source HEAD `12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`

C9 remains the architecture authority. Preserve `REFERENCE_APPROX_SUBENTRY_16` and `SPECULATIVE_CANDIDATE`.

## External concurrent gate

Requires fresh:

`/workspace/m4c-c3-formal-20260905-v1/A_CONCURRENT_RESOURCE_ATTESTATION.txt`

with first line exactly:

`A_CONCURRENT_RESOURCE_GATE_PASS`

and `allowed_c_compile_jobs=1`.

The attestation must be unexpired. It does not mean A is terminal.

## Strict scope

While A remains nonterminal, C may do only:

1. compile/link the final C10-A2 translation model directly into tiny unit-test binaries, one process at a time;
2. execute those tiny translation-only binaries after successful compile;
3. fix ordinary compile/link/unit-test integration bugs in the already-authorized C10-A/A2 delta and repeat the same focused canary.

No new architecture feature may be added.

Explicitly forbidden:

- full GPGPU-Sim/Accel-Sim build;
- parallel build or `make -j`/ninja multiworker build;
- simulator workload/replay;
- C5;
- full standard regression;
- F5 implementation;
- trace scan/generation;
- KV/12K/M5.

## Canary targets

Use the already source-local tests against `src/gpgpu-sim/vm_translation.cc`:

```bash
g++ -std=c++11 -Isrc tests/vm_c10a2_static_model_test.cc \
  src/gpgpu-sim/vm_translation.cc -o <fresh>/vm_c10a2_static_model_test

g++ -std=c++11 -Isrc tests/vm_c10a_registered_segment_test.cc \
  src/gpgpu-sim/vm_translation.cc -o <fresh>/vm_c10a_registered_segment_test
```

Then run both binaries only if both builds succeed.

Use `util/vm_tlb/run_c10b0_concurrent_compile_canary.sh` from Framework to enforce the gate and low host priority.

## CPU placement

Perform a read-only per-CPU/topology audit and choose one genuinely idle physical core. Do not use A's current logical CPU or SMT sibling. If Window B concurrent E01 is also active, do not share B's physical core either.

The canary pins only its own child process and runs it with `nice +10` and low-priority best-effort I/O. Never alter A/B processes.

## Resource gate

Before each compile/test, require:

- fresh A concurrent attestation;
- A PID alive and accumulating CPU time;
- `MemAvailable >= max(64 GiB, MemTotal/4)`;
- `SwapFree >= max(512 MiB, SwapTotal/4)`;
- no swap-in/out during the sample;
- host idle CPU >= 8%;
- iowait <= 5%.

Any failure is `RESOURCE_DEFERRED`.

## Debug policy

If compilation or a tiny test fails, do not stop at the first error. Root-cause the current C10-A2 delta, make the smallest integration/correctness fix consistent with C9, run static checks, re-run this same canary under a fresh resource gate, and checkpoint the fix explicitly.

Do not use a compile failure as an excuse to redesign C9 or add F5/new mechanisms.

## Reuse in later C10-B

A PASS may be cited later as focused evidence for the exact tested SHA, but post-terminal C10-B must still perform its required full compile/link admission and standard regression. This canary cannot unlock C5.

## Final states

Use exactly one:

- `C10B0_CONCURRENT_FOCUSED_CANARY_PASS`
- `C10B0_CONCURRENT_RESOURCE_DEFERRED`
- `C10B0_CONCURRENT_COMPILE_OR_UNIT_BLOCKER`

STOP after the two focused binaries pass or a named blocker/resource defer is recorded. Do not proceed to full build, C10B-1, F5, or C5.