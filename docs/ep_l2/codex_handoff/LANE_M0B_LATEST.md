# Lane M0b Latest

Status: `M0B_PREFINAL_9OF10_REVIEW_READY`

The promoted M0a+M1 parent is `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`
(Core) and `d61ffd23c926a25fa463a3e6e955c885b45f0f8a` (Framework runtime).
M0b ON evidence is frozen at Core `9907b7e617ea0ee6580fb8156e985838720f08fa`
and Framework `8a0299cab19a658d34b7a2dc0b6d91e8373c121b`.

Nine required M0b units are now `COMPLETE_VALID` (six ON observations plus
the three required OFF controls).  All available OFF/ON pairs are exactly
equal in cycles, instructions, and deterministic parsed B0/L1/DRAM artifacts.
The M0b parser still reports 64 physical slices and unsupported terminal
milestones explicitly `NOT_EMITTED`.  Pre-final source/evidence labels are:

- `UNCERTIFIED_CANDIDATE_ONLY` for RO (no source-proven safe eligibility)
- `NO_OLD_RESIDENT_PAYLOAD_HANDLE_HOLD_TO_SET_DONE_OBSERVED` for completed
  dirty-victim data
- `NO_REAL_NONRESIDENT_CONSUMER_OBSERVED_9OF10`

The only live required unit is the isolated scan ON process at
`/workspace/results/ep_l2_m0b/smoke/M0A_ON_M0B_ON_M1_STATIC/scan` (PID 2545913
at checkpoint). It has not been stopped, restarted, duplicated, moved, or
rebuilt under. The only intended ON/OFF config delta is
`-gpgpu_ep_l2_m0b_stats 0 -> 1`.

Review material: `docs/ep_l2/review_packs/M0B_OPPORTUNITY_PREFINAL_9OF10_r1/`.
This is not `M0B_OPPORTUNITY_LOCAL_COMPLETE`; after scan ends naturally I will
parse only that existing output, rerun the read-only aggregate/control checks,
and publish a small-delta final review pack.
