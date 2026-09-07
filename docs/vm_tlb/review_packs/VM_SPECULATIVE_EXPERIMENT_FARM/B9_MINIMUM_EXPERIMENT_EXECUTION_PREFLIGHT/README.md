# B9 minimum-experiment execution preflight

**Final status: `EXECUTION_PACK_READY_AFTER_A_TERMINAL`**
**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

This pack freezes B8 E01--E10 without executing them. It contains 12 exact
E01--E06 simulator smoke arms, two single-job RSS calibration arms, and two
16-kernel static-mining arms. All planned evidence stays speculative.

`util/vm_tlb/run_b9_e01_e10_after_a_terminal.sh` defaults to dry-run. Actual
execution requires both `--enable-execution` and an external file containing
exactly `A_TERMINAL_CONFIRMED`; it is sequential, resource-gated, and refuses
arm-output overwrite. Publishing this pack does not authorize execution.

The A checkpoint was read only through `git show` at its supplied commit. No A
or C private worktree, scratch, process, config, binary, log, or manifest was
accessed. No simulator, worker, trace generator, rebuild, E01--E10 run, or
full ROI scan occurred in B9.
