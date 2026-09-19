# Repair semantic contract

Immediately before each positive/zero-latency L1D or bypass-ICNT downstream admission, the exact `accessq_back()` must already have `vm_translation_applied`. Otherwise the queue remains intact and returns existing `COAL_STALL`; next memory cycle applies the pre-existing translation helper. No TLB/cache configuration, address, coalescing, or scheduling policy is changed.
