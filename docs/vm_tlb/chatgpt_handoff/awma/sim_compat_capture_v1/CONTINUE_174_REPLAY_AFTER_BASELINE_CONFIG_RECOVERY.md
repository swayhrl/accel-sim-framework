# Continue 174 replay after frozen base-config recovery

After recovering `C11_C5_PREFILL_F0.config` from accepted Framework authority and confirming SHA256 `16f9f1866a541ac5686a02f15b8f3abf5fd8723601ff8795db77a64fffb8d446`, continue the existing first-current-model Goal without another checkpoint. Use the accepted current consumer/hotfix implementation to run two identical fixed 10000-cycle replays, close determinism/telemetry, issue SIM_RUN_ID and SIM_EVIDENCE_ID, and stop at `FIRST_CURRENT_MODEL_BASELINE_SIM_PASS`.
