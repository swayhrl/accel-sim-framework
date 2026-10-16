# review_r3 guarded warmup repair handoff

Candidate source is exact Core a9457986625ad44c27229afc3f61dbabbada3e53.
NOT COMPILED / NOT QUALIFIED. Clock-only 1565f1f0 runtime PASS does not qualify this source.
R0 runtime and test patches apply separately to exact R0 parent126394be; R1 adapted combined patch applies to exact be651ccf and retains ideal targets. All three read-only git apply --check calls PASS. No foreign worktree was changed.

Lane1 alone integrates/builds the official R0.1 release after shared resource admission plus build growth headroom. Lane5 independently validates that official release; no second full build. Delta from prior832d986b is included for the in-progress intake. These patches are alternatives, not cumulative.

Initial untimed host initialization is the supported scope. Later GPU epochs, dirty victims, reserved/transient data are explicitly rejected before mutation. Real Tag fill must select the exact checked index and preserve a matching live payload owner. Multi-sector/repeated warmup and warm-read version-zero checks are in the producer test. Four negative cases reject later host use, including after real dirty write/WB pressure; they do not independently cover every internal assertion. Static guards are not runtime PASS.

Fourteen planned cases and exact invocation schema are in PLANNED_PRODUCER_CASES.json. Positive cases must also pass actual response identity, WB/lower/set_done, drain, and <=1 grant per bank/physical cycle; old nine gates need source-delta audit and affected regressions. No official binary/config identity exists for this candidate. Old R0/R1 and every frozen result remain intact.
