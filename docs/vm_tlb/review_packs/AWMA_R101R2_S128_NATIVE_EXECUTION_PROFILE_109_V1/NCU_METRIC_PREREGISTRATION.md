# NCU metric preregistration — RTX4080/SM89

Query authority: `/data/c16/awma/r101r2_s128_native_profile_20260929/raw/ncu_supported_all.txt` SHA256 `2d260b923d0e5e2acb689ff2824b7279c4b91c7dbdbde7b689ea58935868b817` and launch query SHA256 `2f0aa809d91c4e0e5840ef79cc363fe574d8fca365da3162a5d7b705de7f0e1d`. Installed version: `NVIDIA (R) Nsight Compute Command Line Profiler
Copyright (c) 2018-2025 NVIDIA Corporation
Version 2025.1.1.0 (build 35528883) (public-release)`. Device: `NVIDIA GeForce RTX 4080, GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59, 580.178.04, 8.9`.

The exact supported set is frozen in `NCU_METRIC_SET.json` and every requested quantity, including `UNSUPPORTED` entries, is recorded separately in `NCU_METRIC_BINDING_PREREG.tsv`. Counters are warp-instruction or hardware transaction metrics as named; they are not silently equated to per-thread instructions, bytes, or timing. Add only additive counters across launches; occupancy, eligible warps and launch resources remain per-kernel/family weighted descriptives. This is one bounded, source-motivated metric-engineering retry per arm: ATTEMPT0 omitted the supported LDGSTS warp-instruction counter and is archived. The LDG/LD counter and LDGSTS counter are kept as distinct measured quantities; their sum, when shown, is labeled as a derived combined global-read issue count. NCU replay duration is not a timing authority.
