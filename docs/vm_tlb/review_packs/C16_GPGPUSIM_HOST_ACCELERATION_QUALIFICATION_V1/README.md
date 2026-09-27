# C16 GPGPU-Sim host acceleration qualification V1

Final status: **`HOST_ACCEL_NO_SAFE_MATERIAL_GAIN`**.

No host candidate produced a repeatable, end-to-end gain of at least 5% against the current or a pristine same-build authority. The only source candidate was exact on the bounded real-trace prefix but slower, so it was reverted. `C16_GPGPUSIM_HOST_FAST_V1_QUALIFIED` is **not** granted and no optimized binary/config is admitted for B8/B24/BFULL.

## Headline results

- Current authority binary median: 6.121070993 s.
- Pristine same-build median: 6.528739090 s.
- Rejected committed candidate, config=1 median: 7.055922120 s.
- Rejected provisional `HOST_FAST_V1`, config=0 median: 7.161037644 s.
- Candidate B config=0 versus its own config=1: **-1.49%**.
- Combined versus pristine same-build: **-9.68%**.
- Combined versus current authority binary: **-16.99%**.

All admitted 16-kernel comparisons are exact for kernel sequence, per-kernel cumulative cycles/instructions/CTA, normalized full simulator stdout, and terminal receipt. The final cumulative tuple is `(cycles=87146, instructions=613280, CTA=57)`. This prefix contains no completed target range, so victim/allocation/protection decisions were not observable; no stronger target-decision claim is made.

## Read order

1. `QUALIFICATION.json` — machine-checkable medians, speedups, equivalence, receipt hashes.
2. `PERF_PROFILE.md` and `HOST_PROFILE.json` — Phase 0 evidence and limits.
3. `CANDIDATES.tsv` — A–F and combined decisions.
4. `EQUIVALENCE.md` — exactness boundary and observational-output differences.
5. `SOURCE_AND_BINARY_PROVENANCE.json` — authority, candidate/revert, and binary closure.
6. `REPRODUCIBILITY.md` — commands and raw artifact locations.
7. `FUTURE_RUNNER_CONFIG_OVERLAY.config` and `FUTURE_RUNNER_POLICY.md` — no-op scientific overlay and future policy.
8. `RESTART_ASSESSMENT.md` — current-primary status and no-restart conclusion.

Raw simulator outputs remain outside Git under `/root/share/mnt164/huangrulin/c16_ai_workload/host_acceleration_v1/qualification_runs`; their receipt hashes are closed by `QUALIFICATION.json`.
