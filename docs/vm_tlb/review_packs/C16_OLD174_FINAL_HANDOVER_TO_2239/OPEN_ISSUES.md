# Open issues

None of the following is a material blocker for the V0 old174 handover.  Each
is an explicit gate for a later, separately authorized action.

1. `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED` remains the V2A result for the
   missing Llama five-file historical bundle.  V2C is an adopted future-use
   authority only; it must never be presented as a recovery of those receipts.
2. Qwen3-8B and DeepSeek-V2-Lite have hash-closed model assets but
   `NO_HISTORICAL_FROZEN_BINDING`.  A new capture needs a newly recorded input
   binding, not a reconstructed one.
3. Qwen3-30B-A3B has only a recorded, intentionally uninspected metadata
   source.  It has no V0 payload manifest, frozen input binding, trace, or
   migration authority.
4. RTX4080 R5 raw/NCU path availability must be reconciled on node109 before
   archival transfer.  This does not alter clean R5 authority and does not
   authorize a rerun.
5. RTX3090 Route-B remains 34/36 exact.  The two required CUTLASS rows are
   `FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED`; representative selection
   remains blocked, and canary/formal capture remain unauthorized.
6. Any future transfer must use copy-not-move and close source and destination
   SHA256/size.  The proposed node164 path is a planning candidate, not a V0
   action or a verified mount.
