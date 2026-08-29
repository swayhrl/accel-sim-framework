# Banked attribution hold

The 22-of-26 provisional package is retained as a descriptive snapshot, but
its B0-Banked performance and `bank_conflict`/`block_bank` comparisons are not
valid architecture evidence.  See [C6_BANK_ARBITRATION_AUDIT.md](C6_BANK_ARBITRATION_AUDIT.md): the current C6 implementation adds an idle-bank
staging/retry cycle and counts it as a conflict.  Do not use the Banked
performance deltas for EP-L2 mechanism claims pending the audited correction
and reruns.
