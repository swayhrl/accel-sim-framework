# RTX4080 / Ada Accel-Sim Platform Qualification 174-new V1 Report

Qualification result: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`.

The RTX4080/Ada candidate was implemented from reviewed upstream SM89 support and the closest Ada scaffold, with public RTX4080 scale substituted explicitly. It cold-built and terminally replayed all platform anchors, M0, M1, and one AI T2 trace with no unsupported opcode in the exercised subset. This is subset admission, not full Ada ISA fidelity.

V0 used public 76-SM / 64-MiB-L2 / 256-bit / 22.4-Gbps / 2.505-GHz scale. Exactly two calibration passes were used: L1 latency 39->32, fixed L2/ROP latency 187->0, and DRAM latency 254->190. Final calibration errors are 4.50% (P_L1), 21.78% (P_L2), and 18.74% (P_DRAM), with correct hierarchy direction. P_BW Native is 609.014 GB/s, but its 4K-element trace is not comparable to the 67M-element Native timing and was not used to tune.

Held-out validation is insufficient and above threshold. H_CACHE preserves scale but has 43.48% runtime error. H_STREAM and H_COMPUTE shrink workload size by 16,384x and 1,024x respectively, so their trace runtimes are invalid as error points. The required three-point held-out median cannot be computed honestly.

The best candidate is frozen after pass 2, but no `RTX4080_ADA_ACCELSIM_BASE_V1` is promoted. Phase-K AWMA 10/80 overlay smoke is skipped because it is authorized only after PASS or scoped PASS. Recovery requires corrected held-out evidence and a no-tuning replay of the frozen config.

Review pack: `docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/`.
