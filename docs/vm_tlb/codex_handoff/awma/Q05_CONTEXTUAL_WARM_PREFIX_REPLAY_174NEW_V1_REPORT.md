# AWMA Q05 Contextual Warm-Prefix Replay 174-new V1

Status: `AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

The independently rehashed 35-member same-run context bundle was admitted on 174-new. All six required fresh-process rows completed under unchanged accepted F0. No mechanism sweep, full-ROI claim, native↔simulation calibration, or simulator semantic change was performed.

## Main result

| Row | Q05 cycles | L2 TLB misses | Walk starts | L2 data misses |
|---|---:|---:|---:|---:|
| Isolated | 885681 | 633 | 240 | 1183970 |
| P1 | 895312 | 510 | 184 | 1180646 |
| P2 | 848511 | 415 | 128 | 1173919 |
| P4 | 872569 | 450 | 128 | 1175927 |
| P8 | 835145 | 292 | 16 | 1183770 |
| P16 | 862623 | 241 | 16 | 1181047 |
| P34 | 871835 | 249 | 15 | 1190722 |

Translation-relevant coverage reaches 98.678% (64 KiB) at P8. Modeled walk starts drop sharply by P8, but P16/P34 increase cycles again despite nearly unchanged coverage. This confirms that page-set overlap is not equivalent to modeled TLB residency and that longer history can perturb persistent modeled state. The cycle effect is a combined F0 context effect; L2 cache counters are reported, so no translation-only causal claim is made.

The shortest observed contextual row in this matrix is P8, but this is an empirical result under this accepted model—not a hardware-residency claim or authorization for a mechanism experiment.

Raw telemetry, receipts, configs and inputs reside under `/root/share/mnt164/huangrulin/awma_q05_contextual_warm_prefix_replay_v1/`. Review-pack hashes close the small evidence set. STOP here for scientific review.
