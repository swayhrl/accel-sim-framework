# AWMA simulator-native producer report — node109

Decision: `SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS` and `TERMINAL_PROTOCOL_SM89_RECOVERED_V2`.

Run/capture ID: `C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9`. Existing R3 was promoted without recapture because its actual execution—not its historical canary label—met the formal contract.

READY was independently verified/admitted by 174-new. Destination raw path: `/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen25-05b_s2-text_prefill_awma-routeb-sim_q05-prefill-attn-flash_20260917T163000Z_e46193b94dd9`.

Key hashes: kernelslist `674a9c8c0c37027523a91fdcdefa1e690f20012afdb6d05f66e0031837e75602`; trace-member root `00fe079c21a68664727a8c3a48f8776e1d98e1146ba26291194e365af18aaa12`; bundle manifest `fb8a5b9d4923610bb7cf1e10931988747b241df9133257cfbc7c2e88509496f3`; terminal receipt `6e6e483e1dbf44bc522f9d0e8b980397df85a6cf1c8d8048360e350caa1cce72`.

Q05 target: exact Qwen2.5-0.5B revision `7ae557604adf67be50417f59c2c2f167def9a775`, S2_TEXT/PREFILL/B1/T2048/D32/FP16/SDPA, `Q05_PREFILL_ATTN_FLASH`, semantic function occurrence 0. Terminal was COMPLETE with 13,490,624 raw records, zero drop/overflow, and mode2=0. Hotfix validator commit `fb5d0bebee421a0153661239e1f7c2bc088d5c9e` passed the complete trace and accepted 16,128 LDGDEPBAR controls.

Producer scope ends here; no SIM_INPUT_ID or simulation ran on node109.
