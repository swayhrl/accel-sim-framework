# AWMA Discussion Reference — Real Contextual Warm-Prefix Replay

Date: 2026-09-18

## 1. The context-realism question can now be tested directly

The project now has a formally admitted same-run simulator-native sequence for all 34 real Prefill predecessors plus Q05.

This removes the largest previous realism uncertainty:

```text
independent isolated Q05
vs
real same-run predecessor history -> Q05
```

The context bundle is hash-closed and durable on node164.

## 2. The LDC.U8 blocker is closed without inventing trace data

The real P34 capture exposed `LDC.U8` as width-zero/no-dynamic-address.

The recovery did not write `width=1`.

Instead, accepted source showed a pre-existing contract:

- producer ignores constant operands without NVBit MREF;
- serialized LDC can therefore have width 0/no address;
- trace parser creates no memadd payload for width 0;
- trace-driven handles `OP_LDC` through its existing constant-space approximation with hardcoded `data_size=4`.

The strict validator was corrected only for exact `LDC`.

This is a validator/contract alignment, not a claim that LDC.U8 is accurately modeled as a one-byte constant-memory transaction.

## 3. Why the producer page-overlap curve is scientifically interesting

The same-run broad trace-address overlap rises in a highly structured way:

```text
~25%  by P1
~49%  by P2
no increase at P4
~99%  by P8
very small increments after P8
```

This suggests that Q05's address working set is heavily related to very recent predecessor activity.

But it does not yet prove TLB warmth.

A page may have been touched but evicted from the TLB before Q05. Conversely, a page-table prefix may remain useful even when the exact page translation is not resident.

## 4. Why P4/P16/P34 must still be simulated

P4 has the same broad overlap as P2, and P16/P34 add very little overlap beyond P8.

It would be tempting to drop these rows.

Do not.

The extra predecessor kernels may introduce **pollution/eviction** without adding overlapping Q05 pages. Therefore:

```text
same overlap != same target-entry microarchitectural state
```

Comparing P2 vs P4 and P8 vs P16/P34 directly tests this effect.

## 5. Translation-relevant page scope must be recomputed

The producer distance table includes low-address pages such as `0x0`.

The accepted VM hook in `ldst_unit::memory_cycle()` applies translation only to:

```text
global_space
local_space
param_space_local
```

Shared, constant and other non-VM paths must not be used to motivate TLB overlap.

Therefore 174 will recompute 4KiB/64KiB overlap from the admitted bundle using the simulator's actual trace-driven memory-space resolution.

The producer tables remain valid as broad same-run trace-address overlap; they are not overwritten.

## 6. F0 context semantics that matter

The contextual experiment intentionally keeps the accepted F0 behavior unchanged:

```text
L1 data cache: flushed at kernel completion
L2 data cache: not flushed by F0; may persist
L2 TLB: persistence directly demonstrated by self-warm
L1 TLB: persistent by source lifetime unless an explicit translation flush occurs
PWC: persistent by source lifetime, runtime residency not directly dumped
MSHR/PWQ/walkers: drained at clean kernel completion
```

Therefore a contextual Q05 cycle change is initially a **combined modeled context effect**.

Translation and L2-data-cache counters must be compared before assigning cause.

## 7. What result would change the research direction

Three broad outcomes are possible:

### A. Translation cost collapses under real context

If P1/P2/P8 sharply reduce Q05 walks/TLB misses and the contextual baseline becomes much faster, isolated-Q05 translation opportunity was materially cold-start amplified.

Future mechanism work must use an accepted contextual prefix.

### B. Translation remains expensive despite high predecessor overlap

Then the isolated result is substantially strengthened: real predecessor history does not remove the modeled translation bottleneck.

The next mechanism decomposition can proceed with stronger motivation.

### C. Cycles change mainly with L2 data cache, not translation

Then initial-state realism matters, but the main effect is data-cache context rather than TLB/PTW.

The translation research claim must be narrowed accordingly.

## 8. Why first-key outcomes are valuable

If timing-neutral telemetry can identify the first Q05 outcome per simulator key `{asid,vpn,page_size}`, we can distinguish:

- key already warm in L1;
- key warm only in L2;
- key requiring a new walk.

That is much stronger evidence than raw page-set overlap.

It is optional only when implementing it would risk timing/semantic neutrality; aggregate TLB/walk counters remain mandatory.

## 9. Mainline handoff

Node174 now owns the active mainline.

Node109 GPU is released and may run only separately authorized preemptible side work. No side work may delay a new mainline GPU requirement.
