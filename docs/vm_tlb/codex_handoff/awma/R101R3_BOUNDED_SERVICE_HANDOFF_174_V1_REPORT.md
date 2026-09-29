# R101R3 bounded service / producer-handoff screen - 174 V1 report

Stage: `AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_V1`

Final state: `R101R3_S1_BELOW_5_PERCENT_H1_NOT_TRIGGERED`

Stage A recovered O2 maximum scheduled/ready depths 1/16, exact kernel4/5/6
boundaries and a transaction-exact region/opcode decomposition without running
the simulator. The per-line/sector ledger finds earlier real producers for
27,594,584 of 27,594,656 measured reads, while correctly refusing to invent an
initial X0 producer or same-kernel runtime order.

S1 restores normal VM, L1, request ICNT and the existing finite L2
subpartition hit/return resources. Its new binary passes exact default-OFF and
explicit-none T2 equivalence, directed/source tests and accepted regressions.

The formal context matches accepted B0 exactly at 2,976,829 cycles. S1 measured
ROI is 2,963,656 cycles versus B0's 2,985,319: a 21,663-cycle or
0.7256510946% improvement, below the 5% survivor gate. S1 serves all
29,937,568 legal transient transactions with no fallback or correctness
violation and reduces measured L2 misses/DRAM reads to 3,209, but material
cycle response does not survive this placement.

Accordingly, H1, L3, FULL5 and a capacity-matched control were not run. This is
the required negative gate outcome, not a claim that all producer-consumer
handoff is impossible.

The completed S1 raw is rc=0, stderr=0, 6/6 coverage, 56/56 gates and full
drain. A hash-bound postprocess-only recovery corrected two extra summarizer
assumptions without rerunning or modifying simulator raw.

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1/`

Durable root:

`/root/share/mnt164/huangrulin/awma_r101r3_bounded_service_handoff_174_v1/`
