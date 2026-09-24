# Batch 1 Route-B identity qualification STOP report

All three pairs stopped at the required census-only exact-identity gate. No canary, formal capture, payload, traceg, postprocessor, grammar validation, or Accel-Sim work ran.

| Pair | Census evidence | Disposition |
|---|---|---|
| A context length | A1 Route-B census completed; producer ledger did not close the accepted GEMV function/grid/block/global identity. | STOP_PAIR_A; A2 not run |
| B batch | B1 Route-B census completed; producer ledger did not close the accepted elementwise function identity. | STOP_PAIR_B; B2 not run |
| C scientific holdout | C1 Route-B census completed; producer ledger did not contain grid `18992,1,1`, block `8,8,1`. | STOP_PAIR_C; C2 not run |

All census-only invocations held `/data/c16/locks/c16_gpu_campaign.lock`; the lock is released. The producer binary was not modified. The observed mismatch is an exact scientific selector/producer-runtime identity failure, so no ordinal was guessed.
