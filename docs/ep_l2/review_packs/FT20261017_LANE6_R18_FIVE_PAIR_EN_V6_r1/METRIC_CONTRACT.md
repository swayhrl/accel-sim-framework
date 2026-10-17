# Metric/source contract

All source paths below bind Core7b8e6ac70b8fe0f1bd37efca11acb5284938825d.

| Output | Raw source / reduction | Meaning and limit |
|---|---|---|
| cycles/instructions | Frozen Framework9bd17f9d parse_ft_terminal.py native cumulative terminal | End-to-end model cycles/active instructions; never slice-summed |
| copy/WB/WBUF/pool/borrow/rollback | EPL2FTV1 SUMMARY, each64 slices once, sum | Completed transfers/milestones vs repeated refusal events kept distinct |
| bank_logical_ops | EPL2B0V1 application_cumulative, sum64 | Unique modeled operations including work before rollback |
| bank_grants | same; per-bank sum cross-check | Successful modeled bank service, gpu-cache.h:2424/2450; at most1/bank/physical cycle by qualified release; no RTL timing inference |
| bank_wait_cycles | same | Sum of completed-operation conflict waits from first conflict to consumed grant, gpu-cache.h:2427; not GPU elapsed cycles |
| c7d_l2_to_dram_full_block | same | l2cache.cc:1326: exact frontend plan wants lower read while L2→DRAM queue full; repeated/overlapping attempts, not total queue delay or unique transactions |
| c7d_dram_scheduler_full_block | same | Scheduler blocked issue attempts; distinguish causal field c7e_dram_scheduler_causal_block and eligible attempts |
| c7e_dram_successful_*_bytes | same | Successful modeled requests' bytes, preserve actual B/U differences; not power |
| dram_channel_* | EPL2DRAMV1 application; final monotonic cumulative snapshot of each32 channels | Never sum kernel-boundary snapshots; byte totals cross-check64-slice observations |
| dram_model_atom_utilization | Sum issued bytes / sum(atom size × channel DRAM cycles) | Model atom-slot fraction, not measured external bandwidth or universal DRAM saturation |
| WAD hazard/full | same | Same-address/order/entry pressure events, independent of payload slot pressure |
| lowerq_max, scheduler_occ_max | max across64 per-slice maxima | Occupancy bound, not global or averaged utilization |

Missing raw fields raise KeyError; none are filled with0. Legacy C1 resident-headroom is excluded. No peak/reservation counter establishes additional tag-visible capacity or an independent elasticity speedup. Full per-slice observations remain in each native intake.
