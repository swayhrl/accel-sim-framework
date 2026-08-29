# C7e schema contract

`EPL2B0V1` retains all prior field meanings and adds named C7e demand and
successful-issue fields.  `EPL2L1V1` is L1D-only.  `EPL2DRAMV1` is
per-memory-channel and has `scope=application` cumulative records plus
`scope=window, interval=5000_cycle` records.

| Ambiguous legacy label | Prohibited interpretation | C7e exact replacement |
|---|---|---|
| `block_descriptor` | descriptor-pool-full | `c7d_descriptor_pool_full_block`; cap remains `c7d_per_address_cap_block` |
| `block_wad` | WAD-full | `c7d_wad_full_events`; hazard fields remain separate |
| `block_lower` | scheduler-full | `c7e_dram_scheduler_full_observed` and `c7e_dram_scheduler_causal_block` |
| `block_payload` | payload-capacity | `c7d_payload_capacity_allocation_denial`; service port is separate |

The parser must never turn an absent producer field into a numerical zero.  It
uses `NOT_EMITTED` instead.  The final analyzer uses:

```text
bank_true_conflict_rate = bank_true_conflict_ops / bank_logical_ops
```

and labels event counts as events, not exclusive blocked cycles.
