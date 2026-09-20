# AWMA Mainline Gate Update — 2026-09-20

Status:

`ASYMMETRIC_MAINLINE_RELEASE`

## Verified 109 state

Remote pause branch:

`hrl/awma-109-moe-causal-closure-scale-20h-v1 @ 0e32ac01b0237d94b39e45b288263e87e1960ccf`

The paused commit contains the frozen schedule, degree authority, PAUSED_STATE and admitted-condition index.

109 GPU/lock is reported idle.

Decision:

`109_MAINLINE_RELEASED`

Track-B Native Cross-view may start now.

It does not depend scientifically on 174's V4 publication files.

## 174 state

The publication blocker is now infrastructure-bound:

`/root/share/mnt164 -> Transport endpoint is not connected`

The immutable V4 closure bundle is unavailable from 174.

Decision:

`174_MAINLINE_BLOCKED_ON_NODE164_STORAGE_RECOVERY`

No new 174 simulation may start.

## Scheduling rule

Do NOT keep node109 idle merely because 174 storage is blocked.

Run in parallel:

```text
109:
  AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1

174:
  AWMA_174_NODE164_MOUNT_RECOVERY_V1
  -> V4 publication repair V2
  -> only then cross-target Simulation
```

The eventual Cross-view synthesis still waits for both scientific tracks.

## Priority

109 Native mainline now has priority over all paused candidate side lanes.

174 infrastructure recovery/publication has priority over all new 174 science.
