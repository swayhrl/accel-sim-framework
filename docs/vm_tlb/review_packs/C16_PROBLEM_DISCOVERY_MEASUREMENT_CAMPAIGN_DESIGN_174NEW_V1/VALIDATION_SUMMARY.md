# Design validation

The generator produced eight schema-checked TSVs with 14 taxonomy rows, eight coverage rows, eight point rows, nine observable mappings, four strong-baseline rows, five oracle/STOP rows (four primary plus conditional translation authority), 11 closed-direction guards and nine asset/runtime requirements. Six directed tests passed: complete point identities/parents; dense/MoE, phase, W4, context and holdout coverage; 20/30-minute caps and Tier2 lock; question/baseline/oracle/STOP joins; closed-direction/unknown guards; predecessor and execution lock.

The eight tables were regenerated in `/tmp/c16_measurement_campaign_design_rerun_174new_v1` and compared byte-for-byte with the pack. This is table determinism only, not experiment reproducibility. `SHA256SUMS` verifies pack, handoff and scripts. `git diff --check`, remote fetch-back SHA/tree and clean-worktree checks are required before STOP.

The spreadsheet-authoring skill's dedicated dependency loader was unavailable in this session. The user-requested artifacts are repo-native TSVs, not `.xlsx`; the deterministic text generator and explicit schema/join tests provide the table-verification fallback. No spreadsheet library or new science tool was used.

Design remains review-ready but execution-blocked: model/input revisions, 109 SM89 strong backends, W4 quantization path, MoE fused kernels, FP8 eligibility, long-context capacity and direct translation timing observable have not been qualified on the target. Any of these gaps can remove a point or close a question; no weak baseline substitution is allowed.
