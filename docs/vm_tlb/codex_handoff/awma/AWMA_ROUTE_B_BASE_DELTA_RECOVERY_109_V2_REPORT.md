# AWMA Route-B base-delta compatibility recovery — node109 V2

Status: AWMA_ROUTE_B_Q05_LDGDEPBAR_CONSUMER_GRAMMAR_REVIEW_REQUIRED.

The mode-2 base_delta incompatibility is fixed in the single shared Route-B formatter: mode 1 remains used when lossless and all irregular packets use mode 0 list_all. R0 proves the old N-1 delta versus frozen N-delta failure. ULDC width-0/no-MREF fixture passes frozen parser unchanged. R1 CPU formatter/frozen-parser regression and R2 live tiny regression pass.

The exact Q05 canary naturally completed with terminal COMPLETE, 13,490,624 records, zero drops/overflows and no mode-2 records. Its frozen strict grammar now rejects LDGDEPBAR at width 0, while the frozen simulator trace_parser itself accepts the exact trace and classifies LDGDEPBAR as ALU/control. The producer cannot satisfy the strict grammar without fabricated address data, opcode mutation, or a frozen-consumer change, all prohibited here.

No formal capture, READY publication, SIM_INPUT_ID, simulation, or mechanism experiment was started.

Review pack: docs/vm_tlb/review_packs/AWMA_ROUTE_B_BASE_DELTA_RECOVERY_109_V2/.
