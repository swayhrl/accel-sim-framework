# Residency Consumer Pre-Resume Audit V2

## Producer preliminary audit

Producer:
`hrl/c16-e1-residency-intervention-109-v1@22d1b98d7f0c213950654fc754be4e7388836de3`

Preliminary remote review confirms:
- capacity census is internally consistent;
- native intervention timing/raw samples support producer ratios;
- semantic NCU traffic shows the registered WARM/SPARSE/DENSE patterns;
- pressure-dose timing shows a large AWQ response by 64 MiB and a very small RAW response;
- CODE down_proj reproduces the dense AWQ timing/DRAM perturbation;
- producer preserves the preregistered partial-support label.

Important interpretation nuance:
- primary up_proj M1 AWQ `WARM_B/WARM_A = 0.937499981...`;
- therefore the preregistered equality-style recovery gate is false;
- WARM_B is faster than WARM_A, not persistently DENSE-slow.
Do not post-hoc change the boolean or final label, but record this nuance.

## Consumer-prep issue found before real producer consumption

Prep branch:

`hrl/c16-e1-residency-intervention-consumer-174new-v1@1beae7f0ed9c1d3de3829a6ff75ff0317ac1f503`

The original `raw_ncu_consumer.py` required input/output SHA receipts to appear inside NCU `SESSION.csv`.

Real producer evidence does not contain those SHAs in SESSION; it contains them in the preserved `*_PROFILE.log` PASS JSON emitted by the exact replay.

Therefore the original 48 synthetic tests did not fully match the real producer artifact split.

This is a **consumer packaging/verification bug**, not a producer scientific failure.

## Hardening

Use:

`hrl/c16-e1-residency-consumer-hardening-v2`

The hardened consumer separates authority correctly:

- SESSION.csv:
  - application replay
  - cache-control none
  - exact NVTX selector
  - exact metric set

- PROFILE.log:
  - exact role/M/implementation/state/range
  - exact input SHA
  - exact output SHA
  - PASS replay receipt

- BASE.csv:
  - exact selected range rows
  - kernel inventory
  - replay pass count
  - byte metrics

Point specs must now include:
- `base_path`
- `session_path`
- `profile_path`

Before final consumption, rerun the entire consumer test suite after merging/cherry-picking this hardening and add a real-artifact canary against at least one producer WARM profile.

Do not silently weaken the identity gate.
