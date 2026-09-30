# Round16 side-lane activation

Date: 2026-09-30

Both primary Round16 lanes have reached STOP:
- Lane G / R102: input authority not qualified, CUDA=0.
- Lane F / VLA VJP: real workload qualified, but architecture state/lifetime residual not qualified.

The previously deferred CCE/Liger exact-loss quick falsification is now activated on the freed **Lane G / node109** window.

Reason:
- a compatible real next-token CE workload/model asset already exists in accepted AWMA/R101 provenance;
- current CCE exposes an exact/no-gradient-filter reference mode;
- current Liger exposes a strong fused linear-cross-entropy implementation on Ada/Triton;
- the experiment can be bounded to one real shape and one operator boundary.

This remains a low-cost falsification side lane, not a new mainline.

Execution Goal:
`LANE_G_EXACT_LOSS_CCE_LIGER_109_GOAL.md`

Execution branch:
`hrl/awma-cce-liger-exact-loss-boundary-109-v1`
