# Three evidence levels — no arithmetic pooling

| Evidence | Aorder→Dready result | Evidence level |
|---|---:|---|
| R22F NSYS, source-attributed resolved net TP family | Dready **+26.752 µs** profiled kernel-duration cost, including real deterministic fixup +30.160 µs | Instrumented family diagnostic |
| R22F1 exact-input low-overhead CUDA-event replay | Dready +0.062 µs saved by median; 5 group gaps [-15.47, 3.224, 0.062, -3.878, 12.788] µs; larger-arm aggregate MAD 7.732 µs | Standalone exact-call family replay, mixed |
| R22F uninstrumented complete OAM-S energy+force | Dready **13.955 µs / 2.878%** faster, CLEAR | Full-model ready-graph boundary |

The exact two real callsites (one per layer) and their real upstream VJPs were used in both arms. Same-input forward/required gradients passed `atol=rtol=5e-5`; 32-state backward canary passed. Forward aggregate gap -0.272 µs and backward aggregate gap +0.334 µs are individually mixed. Callsite combined gaps are -0.039 and +0.243 µs, neither stable.

The direct fixup API was unavailable, so the actual low-overhead fixup-only service time is **UNKNOWN**; the parent 30.160 µs is an NSYS diagnostic, not a measured R22F1 cost. The new family replay does not establish the parent's positive full-model effect as TP-family benefit, nor does it establish that the profiled negative family cost persists without NSYS. Different scheduling, launch gaps and graph context are possible explanations, not proven causes. No Donline or old holdout was run.
