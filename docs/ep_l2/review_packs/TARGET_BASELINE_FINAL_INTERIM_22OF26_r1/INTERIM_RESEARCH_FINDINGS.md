# Interim research findings — 11 complete pairs only

All statements use exact C7e final parser/analyzer fields in `analysis/`. They are interim hypotheses: `gemm` and `3mm` are not estimated or included in an aggregate.

1. **Shared 256-descriptor pool:** it is a real shared pressure point: `vectorAdd_4M`, `scan`, `spmv`, `convolutionSeparable`, `FWT_7_21`, and `FWT_11_19` reach descriptor max 256 and report pool-full events. `btree` reaches 253 with zero pool-full events, so old fixed-merge fragmentation is not observed as persistent btree blocking here.
2. **Descriptor without Line-MSHR saturation:** yes. Those six workloads reach descriptor max 256 while Line-MSHR maxima are 92, 113, 99, 126, 102, and 96; all have measured zero Line-MSHR-full events.
3. **32/address cap:** nonzero only for `spmv` (8,598 Banked events), `sgemm` (1,409), and `btree` (674).
4. **Tag/set:** tag-way blocks are zero except `scan` (222,849), weak relative to its allocation demand; no broad primary Tag/set limit is observed.
5. **WAD:** capacity/hazard is visible: scan has 2,318,944 full and 585,398 hazard events; dwt2d 74,044 full and 19,521 hazards; FWT_7_21 286,123 hazards; convolution 8,266 full; cfd_097k 9,408 hazards.
6. **Payload:** all completed pairs measure zero payload-capacity allocation and service-port denials. This is measured zero, not a missing field.
7. **C6d Banked conflict:** only `cfd_097k` has material true contention: 16,166 conflict ops, 16,166 wait cycles, 0.014784182 true-conflict rate, and 81,443 Banked versus 79,555 Legacy cycles. All other completed Banked runs are measured zero.
8. **L1D:** L1D is a competing observed pressure (scan has 124,523,721 MSHR-entry failures, 38,533,635 MissQ-full events, and 55,242,027 bank/latency conflicts). It does not alone prove masking of a specific L2 opportunity.
9. **Lower path:** scan, vectorAdd, convolution, and FWT_7 show L2-to-DRAM full events plus scheduler-causal blocks. Scan/vectorAdd bandwidth utilization is 0.818652729/0.795837193. ReturnQ and DRAM-to-L2 blocks are measured zero throughout this subset.
10. **Later RO/TVD/Unified:** baseline telemetry contains no eligibility/reuse/complementarity oracle. It may nominate descriptor-heavy workloads (vectorAdd, scan, FWT_7) and cfd bank contention for later shadow study, but cannot claim benefit.

## Evidence discipline

- A zero means the final C7e producer measured zero; it does not mean field absence.
- `TELEMETRY_COMPLETENESS.csv` distinguishes `MISSING_FIELD`.
- 5K window artifacts support burst-versus-sustained follow-up; occupancy is not turned into a causal claim.
