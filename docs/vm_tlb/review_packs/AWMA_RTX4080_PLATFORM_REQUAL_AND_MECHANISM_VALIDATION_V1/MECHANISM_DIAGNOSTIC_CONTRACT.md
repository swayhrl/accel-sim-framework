# Mechanism diagnostic contract

Both diagnostics are independent opt-ins and default OFF.

- `GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1` observes issue cycles at old control PCs `0x240/0x10b0` and separately identified mechanism PCs `0x4a0/0x870`.
- `GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS=1` records active lanes and already-coalesced `accessq_count()` at LD/ST issue.

Neither diagnostic mutates scheduling, scoreboard, accessq, translation, cache/memory requests, replay, or downstream ordering. A1 and A32 Legacy 10/80 OFF/ON scientific signatures match exactly.
