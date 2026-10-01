# AWMA R19F2 — FP8 strong-software counterfactual on real Qwen MLP

Stage: `AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1`

Execution branch: `hrl/awma-r19f2-fp8-software-counterfactual-109-v1`

Starting HEAD: `d83259e7c9085de686216b7de0166776f6254922`

Scientific parent: `7375abd8e86c1523c1873913e8fffccf0b4e3a96`

Final label: `R19F2_FUSED_SOFTWARE_SUFFICIENT`

On one frozen real Qwen2.5 layer0 MLP input, gate/up produce the same E4M3 representation from the same BF16 X. Sharing one ordinary TE quantization was exact but left a `17.29%` ready-pair gap at the complete MLP boundary. The sole allowed exact single-launch fused software diagnostic then reduced that complete-MLP gap below 5% and recovered `84.09%` of the remaining S1→D0 headroom. The preregistered gate therefore closes this operator-level hardware opportunity at a strong *software counterfactual*, without designing a mechanism.

| Complete MLP Region M | B0 duplicate | S1 shared TE | S2 exact fused shared | D0 representation-ready |
| --- | ---: | ---: | ---: | ---: |
| Stage A wall median | 0.195725 ms | 0.182693 ms | — | 0.151110 ms |
| Stage B wall median | frozen Stage A | 0.187174 ms | 0.154272 ms | 0.148045 ms |

The two rows are separate paired campaigns; Stage B does not replace the frozen Stage-A B0/D0 receipts. Each reported arm has 15 unprofiled formal samples, 3 groups, 2 warmups/arm/group, rotating order, plus CUDA-event samples. Stage B's S2−D0 wall residual is `4.04%` of S2 and not stable across all groups; S1−S2 improvement is stable. These are one-MLP operator-boundary times, **not** BF16→FP8, complete-model, or online-request speedups. D0 starts with the FP8 input already ready and is ideal diagnostic only. S2 uses preallocated output/metadata buffers and is not a shipping TE path.

The real X is the accepted R19F1 forward-hook input. Gate/up/down weights are the natural layer0 weights of the same hash-verified Qwen revision; the up weight matches R19F1 bitwise. TE v2.19.0, source `5e52befd5262c06289106338c308079d6adb391f`, current-scaling E4M3 and RTX4080/SM89 remained fixed. Gate/up normal input, shared input and fused input FP8 bytes/inverse-scale all match exactly. All three Stage-A arms and Stage-B S2 produce bitwise-identical gate/up/MLP outputs. The sole new NSYS capture confirmed the same native `sm89_xmma_gemm_e4m3...` gate/up function/grid/block in B0/S1/D0, with 2/1/0 quantizer invocations. No alternate GEMM was written or timed.

This README is the review entry; `FINAL_DECISION.md`, `STAGE_A_DECISION.md` and `STAGE_B_DECISION.md` show each scientific gate in detail. `PARENT_AUTHORITY.json`, `REAL_MLP_INPUT_WEIGHT_RECEIPT.json`, `SHARED_REP_IDENTITY.json`, `FUSED_REP_IDENTITY.json`, the P/M samples, `PROFILE_SUMMARY.tsv` and `SOFTWARE_CAPABILITY_AUDIT.md` close the source/runtime/output identities. `RAW_DATA_INDEX.tsv` locates large payload, compiled diagnostic, numerical objects, complete NSYS/SQLite and logs on node164. `SHA256SUMS` and `RAW_SHA256SUMS` close the compact and raw files.

Evidence labels: TE/Qwen source audits are `VERIFIED_CODE`; frozen payload, exact numerical identities, CUPTI-correlated consumer names and formal timings are `VERIFIED_RUN`. The branch diff adds only the R19F2 source-audit/canary/timing/parser tools, one opt-in diagnostic quantizer, and this review pack; accepted TE/model/driver/simulator sources are unchanged. Open boundaries are production integration and whole-model numerical/latency behavior; neither is inferred here. No NCU, NVBit, SASS, Accel-Sim, node174 computation, hardware mechanism or Blackwell FP4/TMEM claim was made. All GPU actions held the shared 109 lock, which was released after each bounded run.
