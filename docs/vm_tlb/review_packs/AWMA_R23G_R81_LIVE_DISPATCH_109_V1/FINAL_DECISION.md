# Final decision

`R23G_R81_LIVE_DISPATCH_LOCAL_RESPONSE_PRESENT`

Requirements are met:

- the 12-record public validation cohort was frozen before candidate execution;
- old R81 online union counts and RULE_U01 classifications matched exactly;
- all new B0/M1 token trajectories, stop positions, JSON schemas, truncation
  checks, and matcher terminations qualified;
- V0, V1, and V2 each had all three group medians favor M1, with every absolute
  LIVE_HEAD gap larger than three times the larger-arm MAD;
- no batch showed a stable complete-generation regression above 2%.

The fixed CPU union+dispatch cost was fully included and did not remove the
local response. This is evidence for a bounded dense/direct-index software
policy and broader software integration testing only. No hardware claim or
automatic next mechanism is authorized.
