# Accessq cardinality diagnostic contract

`GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS=1` is an independent observational switch, parsed once by `awma_accessq_cardinality_recorder`. Default/off emits nothing. At `ldst_unit::issue`, after coalescing has populated `accessq` and before any entry is consumed, it records each active global load's kernel UID, SID, warp/dynamic warp, PC, active lanes, accessq cardinality, and monotonic event ID under prefix `awma_accessq_cardinality_`.

The helper does not modify scheduling, coalescing, accessq, translation, cache, retry, timing, random state, or downstream order. M1/M2 C0→C1-off and C1-off→C1-on scientific outputs are exact matches.
