# Validation

Frozen Core source: `56abbacc1192d68995e78561899719649f838079`. Seven groups pass in each of normal and ASan+UBSan builds. No assertion or lifecycle check was removed to obtain PASS. The first standalone compiler failure was a legacy initializer-order warning promoted by -Werror; it was resolved only in the isolated runner, preserving the warning in logs.

Commands from Core worktree:

```bash
EP_L2_SANITIZE=1 EP_L2_LANE2_BUILD="$PWD/build/ft20261016_lane2_dirty_sanitize" tests/ep_l2/run_tvd_directory.sh
EP_L2_SANITIZE=0 EP_L2_LANE2_BUILD="$PWD/build/ft20261016_lane2_dirty_normal" tests/ep_l2/run_tvd_directory.sh
```

Real cache/trace tests: NOT_RUN; producer integration and qualified Lane 1 runtime not published. Formal performance rows: zero. This dependency is not an assertion about a scientific failure or absent TVD opportunity.
