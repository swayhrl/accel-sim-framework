# C6d + C7d closeout

Stage: C6d + C7d closeout
Status: CONDITIONAL PASS

Core final SHA: `88e243e8e421002079adc85b9efae3452c02a828`
Framework final SHA: `2aef9fad48207415a9697f9b891068b42008e0a8`

Main conclusions:

- C6d removes the unconditional idle-bank staging/retry; the four smoke pairs
  are terminally valid and show zero residual Banked penalty where measured
  true contention is zero.
- C7d provides separately named target telemetry and avoids interpreting old
  coarse counters as exact resource blockers.
- The final 13x2 campaign has not started.

Remaining issues:

- Final-SHA validation evidence is incomplete for the C7d L1 launch-level
  aggregation, instrumentation ON/OFF timing-neutrality, and host-overhead
  measurement. Earlier natural samples use pre-final C7d SHAs and are
  diagnostic-only.

Formal campaign recommendation: NOT READY

Review entry point: `docs/ep_l2/review_packs/C6D_C7D_CLOSEOUT_r1/README.md`

Most important files for ChatGPT:

1. `FORMAL_RUN_READINESS.md`
2. `C6D_CLOSEOUT.md`
3. `C7D_SEMANTIC_FIXES.md`
4. `C7D_FIELD_MATRIX.csv`
