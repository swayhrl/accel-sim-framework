# M4A-C Goal progress

Goal: `M4A_C_FORMAL_CAPTURE`

| Gate | Status | Local SHA | Remote SHA | Evidence / next action |
| --- | --- | --- | --- | --- |
| G0 | BLOCKED | `cc76b6b77ac7b26a3180c77540d9bc18ac83cce6` | `ac9f42f824abb325acec0846b0da6cce78849d56` | Pilot report ended `PILOT_BLOCKED`, so Goal activation is prohibited. Remote host remains the approved 4×SM86 host with 982 GiB free and no GPU compute processes. Resolve gated-model credential under a new P5 handoff. |
| G1–G8 | NOT_STARTED | — | — | Not authorized because G0 is BLOCKED. |

No formal run ID, archive, or copy-back path exists for this Goal attempt.

## Pre-shutdown checkpoint

Created at `2026-09-02T14:05:25Z` before the user powers off the retained
AutoDL instance. The main-server checkpoint is
`/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/`; it contains
the exact remote resume paths, selected small evidence, and 24 successful
remote-to-main-server SHA256 comparisons. The remote work root remains
`/root/autodl-tmp/m4a-llama` and was left intact. P5 remains the next required
gate; this checkpoint neither changes `PILOT_BLOCKED` nor authorizes capture.
