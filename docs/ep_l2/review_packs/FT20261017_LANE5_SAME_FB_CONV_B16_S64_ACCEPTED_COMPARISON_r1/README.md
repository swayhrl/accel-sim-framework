# Same-FB Conv: B16 and S64 accepted endpoints

B16:292932 cycles; S64:293258 cycles; both714547200 instructions. Same exact Core/Framework/binary/full trace/epoch/termination and first five config hashes. Actual per-slice layout is1168 slots and4 banks×1op per physical GPU cycle in both modes; S64 changes staticWB16→64 and bypass128→80.

Observed WB-data-full refusals fall845097→0 while cycles rise326. This is a negative result for this static repartition. Copy work remains; this comparison is not a pure-copy ablation and does not certify an optimal static allocation. Refusal and aggregate bank-wait counts are not elapsed-time components.

Exact current-accepted rows and native raw-log paths are in RECEIPT.json. Use the separately published pressure-identity correction overlays for the historical derived source_core label; actual source manifests/cycles never changed. U_CAP16 and Unified are still required for the complete four-way comparison.
