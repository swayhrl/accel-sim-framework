# R20R3 review after profiler-evidence STOP

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r20r3-active-world-solver-native-109-v1`
- commit: `fa292a11dbc196b65ebe1f3a67f39a7837046995`
- tree: `9511e479de730302282d50c50853caf47d398d50`
- formal label: `R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED`

## Accepted facts

- all four frozen discovery solver entries passed OFF/B0 regression under the revised R20R2-reviewed numerical contract;
- the only authorized NSYS workload replayed t128/t136/t144/t152 successfully and preserved the numerical contract;
- the pre-timing eligible-stage audit was frozen before profiler output inspection;
- the NSYS process returned code 0 but produced no .nsys-rep / SQLite / qdstrm payload;
- therefore cumulative per-stage B0 GPU time is unavailable;
- the predeclared selection rule cannot choose a stage;
- no stage, S1, candidate correctness, formal performance timing or holdout result exists.

This is an evidence-admission / profiling-engineering stop, not an active-world performance negative.

## Likely profiler trigger issue

The R20R3 launcher uses direct `nvtxRangePushA` / `nvtxRangePop` dynamic NVTX strings:
- outer range: `R20R3_PROFILE`
- nested ranges: `R20R3_T{step}_OFF_B0`

The NSYS command used:
`--capture-range=nvtx --nvtx-capture=R20R3_PROFILE`.

Current NVIDIA Nsight Systems documentation states that, by default, only NVTX registered strings are considered for profiler capture-range matching; applications using unregistered NVTX strings must set:
`NSYS_NVTX_PROFILER_REGISTER_ONLY=0`.

This is a strong likely explanation for a workload that completed while no capture report was generated, but the existing evidence does not prove it is the unique root cause.

The receipt also does not show an explicit `-o/--output` path. Future profiling should use a unique absolute output prefix and verify the expected report path directly rather than relying on a default report location.

## Recommended repair — requires new authorization

Do not rerun R20R3 wholesale.

Use a bounded `R20R3P1_PROFILER_ADMISSION_REPAIR`:

### Engineering canary
1. Record `nsys --version` and `nsys status --environment` or equivalent supported environment status.
2. Use the same R20R3 Python/NVTX mechanism and one tiny CUDA/Warp workload.
3. Run NSYS with:
   - explicit absolute `-o` prefix
   - `--force-overwrite=true`
   - `--trace=cuda,nvtx`
   - `--capture-range=nvtx`
   - one exact canary NVTX range
   - `NSYS_NVTX_PROFILER_REGISTER_ONLY=0`
4. Require a nonempty `.nsys-rep`.
5. Export SQLite explicitly with `nsys export --type sqlite` if direct `--export=sqlite` behavior is uncertain for the installed version.
6. Run one simple `nsys stats`/SQLite sanity query proving CUDA kernel rows are present.

This canary is profiler admission only and does not consume or inspect scientific stage timing.

### One repaired scientific profile
Only after the canary passes:
- reuse exactly the same OFF/B0 four-entry workload, order, source, snapshots and numerical checks;
- keep `ELIGIBLE_STAGE_AUDIT.md` and the frozen stage-selection rule unchanged;
- one repaired NSYS collection with explicit output path and validated trigger;
- require report + export + child CUDA kernel rows before considering the profile qualified.

If the repaired collection still does not produce attributable stage timing:
`R20R3P1_PROFILER_NOT_QUALIFIED`
STOP.

If it succeeds:
- resume R20R3 from stage selection using the already-frozen eligible-stage audit;
- select exactly one stage by the original cumulative-GPU-time rule;
- no re-ranking rule, second profiler, second candidate or worker sweep is authorized by this repair alone.

## Scope boundary

Do not infer from the current missing report:
- zero stage time
- no active-world opportunity
- profiler incompatibility with the workload in general

Do not change:
- scientific inputs
- numerical contract
- solver/source
- eligible-stage criteria
- candidate selection rule

Current state:
- R20R3 scientific performance question: UNMEASURED
- candidate: NOT CONSTRUCTED
- holdout: SEALED
- architecture review: NOT READY
- Lane F: STOP pending explicit profiler-repair authorization
- Lane E/G and node174: STOP
