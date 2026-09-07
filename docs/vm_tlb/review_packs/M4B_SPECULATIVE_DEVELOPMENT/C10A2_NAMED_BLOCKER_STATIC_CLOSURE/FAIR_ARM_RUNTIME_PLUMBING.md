# B5 — executable selector and fair-arm manifest contract

`-gpgpu_vm_fair_arm` selects only the C9-defined arms through
`configure_fair_arm()`. It overwrites arm-controlled fields and
`translation_config::valid()` rechecks the realized geometry. The controller
emits arm ID/name, charged symbolic bits, L2 entries/sets/associativity, and
existing Segment configuration/status telemetry.

`configs/vm_tlb/M4B_C10A2_FAIR_ARM_PROFILES.tsv` is the frozen static manifest.
It records the following official selector values:

| Arm | Value | Realized state |
| --- | ---: | --- |
| F0 | 1 | 768 exact, 16-way, 48 sets |
| F1 | 2 | 96 16-leaf groups, 16-way, 6 sets |
| F2 | 3 | 688 exact, 16-way, 43 sets |
| F3 | 4 | caller-supplied charged exact sweep `E>768`, `E % 16=0` |
| F4 | 5 | 1536 exact diagnostic |
| F6 | 7 | 848 exact 2MiB diagnostic |
| F7 | 8 | 320 exact + N=8 Segment x35 local replicas |
| F8 | 9 | 32 16-leaf groups (2 sets) + N=8 Segment x35 local replicas |
| F9 | 10 | 656 exact comparator |

F7/F8 accept only 35 SMs and the existing parameterized `Lseg` points
5/10/20. C10 v1 models Segment acceptance lockstep with successful local-L1
admission: one accepted local L1 port per cycle is the declared Segment
accept-rate/backpressure proxy, with Segment accepts and port denials reported
separately. This is a model contract, not a hardware throughput measurement.
The official F7/F8 lifecycle also requires an accepted V2 ASID/epoch
registration; a historical V1 map can remain available only to manually
reproduce earlier speculative evidence and cannot become a fair official arm.

F5 (value 6) is hard-invalid because the physical PWC model is not present.
H0 (value 11) is hard-invalid forever: no official selector can expose the
historical 768-group artifact. F4 and F6 remain diagnostics, not equal-cost
claims. All sub-entry labels retain `REFERENCE_APPROX_SUBENTRY_16`; F7/F8
remain `SPECULATIVE_CANDIDATE`.
