# Current state

Stage: `S1_B0_BOOTSTRAP`

The VM-core worktrees were created from the frozen Core and Framework bases. The
clean baseline build and the two trace smoke runs passed. No simulator behavior,
configuration, trace parser, or VM/TLB mechanism was changed in this stage.

The Core worktree has no verified writable remote. This is the remaining bootstrap
blocker; see the Codex report and S1-B0 review pack for the recorded evidence.
