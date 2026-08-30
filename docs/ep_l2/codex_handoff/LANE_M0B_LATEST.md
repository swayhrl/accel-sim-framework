# Lane M0b Latest

Status: `M0B_INTERIM_REVIEW_READY`

The promoted M0a+M1 parent is `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`
(Core) and `d61ffd23c926a25fa463a3e6e955c885b45f0f8a` (Framework runtime).
M0b ON evidence is frozen at Core `9907b7e617ea0ee6580fb8156e985838720f08fa`
and Framework `8a0299cab19a658d34b7a2dc0b6d91e8373c121b`.

`convolutionSeparable` ON is `COMPLETE_VALID`; parser cardinality is 64
physical slices and unsupported terminal milestones are explicitly
`NOT_EMITTED`.  Preliminary source/evidence labels only:

- `CURRENT_MODEL_DOES_NOT_RETAIN_OLD_RESIDENT_PAYLOAD_HANDLE_TO_SET_DONE`
- `PRELIMINARY_NO_REAL_NONRESIDENT_CONSUMER_OBSERVED`

The exact OFF counterpart remains live at
`/workspace/results/ep_l2_m0b/smoke/M0A_ON_M0B_OFF_M1_STATIC/convolutionSeparable`;
it has not been stopped, restarted, duplicated, moved, or rebuilt under.
The only intended ON/OFF config delta is `-gpgpu_ep_l2_m0b_stats 1 -> 0`.

Review material: `docs/ep_l2/review_packs/M0B_OPPORTUNITY_INTERIM_r1/`.
Maturity remains `SPECULATIVE_PENDING_GATE`; no final M0b conclusion has been
made.
