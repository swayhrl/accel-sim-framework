# START HERE — AWMA R22F1 low-overhead OEQ family replay

Date: 2026-10-02

User authorization: inherited from the approved post-Round22 plan.

Scientific parent:
`df0e8edd009ee1a56ba65b25b319e8a852f74d27`

Parent status:
`R22F_R21A_FAMILY_RESULT_MIXED`

Why this follow-up exists:

- source-attributed NSYS says deterministic OEQ gross TP improves but mandatory deterministic fixup makes the profiled net target family ~26.752 us slower than Aorder;
- uninstrumented complete energy+force says Aorder -> Dready is ~13.955 us / 2.878% faster and CLEAR;
- non-target profiled response is essentially neutral;
- therefore the sign mismatch must be resolved before any Donline, holdout or hardware claim.

This Goal performs one low-overhead same-input OEQ family replay using exact tensors captured from the real OAM-S discovery computation.

Execution branch:
`hrl/awma-r22f1-oeq-lowoverhead-replay-109-v1`

Lane F / node109 only.
No NSYS, NCU, NVBit, SASS, Accel-Sim or node174 compute.
