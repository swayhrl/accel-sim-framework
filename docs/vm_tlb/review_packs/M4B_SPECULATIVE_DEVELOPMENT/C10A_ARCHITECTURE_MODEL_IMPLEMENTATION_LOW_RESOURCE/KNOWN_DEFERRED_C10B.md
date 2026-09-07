# Named C10-B blockers and required next validation

| ID | Blocker | Why it blocks replay/full PASS | Required C10-B action |
| --- | --- | --- |
| B1 | Final Core `c27bf0e2` is unbuilt/unlinked/unrun | static inspection cannot prove C++ correctness or standard-mode preservation | resource-gated `-j1` focused build/run, then required regression subset/full build |
| B2 | V2 invalid/overflow/overlap registration aborts during parse rather than returning an explicit atomic all-replica conventional-fallback outcome | M3 driver-transaction contract is not realized | transactional registration result/state; test 9th extent, overlap, bad metadata and no partial live image |
| B3 | No runtime install/revoke/epoch-generation/ack state machine | stale descriptor protection across remap/free/context lifecycle is incomplete | driver/runtime lifecycle, replica acknowledgements, epoch wrap/quiesce and stale-hit tests |
| B4 | Simulator caller integration currently defaults to READ access intent | real store/atomic traffic may not yet supply its true access class | wire production translation call site and test write/atomic route end-to-end |
| B5 | `num_sms=35`, Lseg 5/10/20 and F0--F9 TSV are contract metadata, not parser/manifest-selected runtime profiles | arms are not execution-ready | config parser/manifest export with explicit profile guards and runtime configuration tests |
| B6 | Local replicas are immutable copies, not independently acknowledged hardware state | topology/lifecycle model incomplete | model per-cluster install/revoke acknowledgements and context state |
| B7 | No captured sub-entry ASID generation/stale-fill discard | shootdown race can resurrect translation | add generation to fill transaction and race tests |
| B8 | F5 physical PWC pointer payload, banks, port/queue/timing not implemented | legacy 128-entry PWC cannot be called equal-budget F5 | implement C9 F5 state/port model or retain hard block |
| B9 | No post-delta cross-layer telemetry output inspection | schema continuity cannot be empirically established | focused output parser plus full C10-B regression before any replay |

No blocker is an architecture contradiction. C9 remains internally coherent;
these are intentionally uncompleted engineering/runtime-validation items.
