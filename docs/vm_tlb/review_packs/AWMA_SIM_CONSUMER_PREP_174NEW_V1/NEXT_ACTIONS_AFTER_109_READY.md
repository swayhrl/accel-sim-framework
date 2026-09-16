# Next actions after the producer is ready

Proceed in this order, without substituting Native C16WARP1/MREF bytes:

1. Independently rehash every producer bundle member and its canonical root.
2. Verify the producer terminal receipt is `COMPLETE` with zero drop/overflow.
3. Verify the exact accepted model, revision, input, runtime, phase, target, and launch binding.
4. Run formal admission, `xz -t`, and the real official traceg grammar smoke for every listed trace.
5. Issue a stable `SIM_INPUT_ID` only after all admission gates pass.
6. Preserve producer bytes immutable; derive and hash a compatibility view only where path/config adaptation is necessary.
7. Run the accepted `NEW_SIM_BASELINE_V1` fixed 10000-cycle replay with `fixed_window_replay.py`.
8. Repeat the identical run and compare receipts for determinism.
9. Normalize and hash telemetry, retaining raw logs.
10. Issue `SIM_RUN_ID` and `SIM_EVIDENCE_ID` only from complete receipts.
11. Record the Native-to-Simulation relation only as `EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE`.

Do not perform Native-versus-Simulation numerical calibration, full-ROI claims,
or mechanism sweeps in that continuation unless separately authorized.
