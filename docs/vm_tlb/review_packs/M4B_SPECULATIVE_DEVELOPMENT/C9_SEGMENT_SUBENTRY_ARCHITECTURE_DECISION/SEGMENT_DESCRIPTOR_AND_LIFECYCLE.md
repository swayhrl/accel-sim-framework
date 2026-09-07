# Segment descriptor installation and lifecycle

## Authority and eligibility

`USER_APPROVED_DIRECTION` and `C9_MODEL_DECISION`: the serving runtime may request registration but
has no authority to make a VA accelerator-eligible. Only a privileged GPU driver / VM manager may
create, replicate, revoke or invalidate a descriptor. The simulator object map is retained only for
post-hoc telemetry attribution and cannot participate in Segment match, replacement or timing.

Registration request ABI:

```
register_weight_region(asid, allocation_handle, requested_va_range, read_only=true)
```

The driver validates all of the following before descriptor construction:

1. allocation ownership and the requesting ASID/context;
2. requested range lies within the allocation and contains only pages owned by it;
3. read-only/PTE access eligibility and allowed memory attributes;
4. 64KiB mapping class and physical-page continuity per resulting extent;
5. page pinning for the complete active inference epoch;
6. extent count `1..8`, non-overlap and no descriptor collision in the ASID table;
7. capacity in every local replica and a successful atomic broadcast path.

Any rejection returns `REGISTRATION_FALLBACK_CONVENTIONAL`; it does not install a subset, alter the
ordinary page table, or label a request `OBJECT_WEIGHT`. The runtime may proceed with inference using
normal paging or decline the model load. This is a performance fallback, not a permission override.

## Pinned immutable inference epoch

`PAPER_SPEC`: weights are read-only and resident during serving. `C9_MODEL_DECISION` uses that
property to deliberately constrain v1, rather than claim arbitrary dynamic remapping support.

```
model load
  -> allocate/map and make Weight pages read-only
  -> driver discovers full-page physically contiguous extents
  -> pin extents, assign next nonzero (ASID, epoch)
  -> validate and broadcast all descriptors to 35 local tables
  -> all-table acknowledgement
  -> inference epoch (descriptors immutable; one local lookup/cycle)
  -> quiesce context and drain/cancel join tokens
  -> revoke descriptors + Segment/L1/L2 shootdown acknowledgement
  -> unpin, remap, free, model unload, or ASID reuse
```

`valid` becomes visible only after installation acknowledgement. The active ASID epoch must equal the
descriptor epoch on every hit. Epoch value zero is invalid. If a 16-bit epoch would wrap, the driver
performs an ASID-global quiesce and invalidation acknowledgement before reuse; it cannot silently
reuse a numeric epoch with outstanding translations.

## Invalidation, migration and context semantics

| Event | v1 driver action | Required observable correctness result |
| --- | --- | --- |
| model unload / free | quiesce, revoke descriptor replicas, invalidate Segment and conventional TLB state, await acknowledgement, then free | no post-free PA is returned. |
| page migration/remap | not allowed while epoch is active; first revoke and ack, then remap/pin/register a new epoch | no request hits old PA. |
| UVM ownership/fault | revoke or reject registration before ownership changes; ordinary VM handles fault | Segment never bypasses ownership protocol. |
| PTE permission change | revoke and shoot down before change becomes visible | Segment rights cannot exceed ordinary PTE rights. |
| context switch | ASID remains a hit key; context scheduling alone does not change a valid epoch | no cross-context descriptor match. |
| ASID reuse | revoke/flush/ack all old state before assigning a new epoch | old descriptor cannot hit in new address space. |
| descriptor capacity / broadcast failure | atomically leave all descriptors invalid for that registration | all requests use conventional paging; no partial cluster behavior. |
| L1/Segment mapping mismatch | stop architectural completion for uncompleted request; record fatal consistency event; quiesce context per error policy | mismatch is never silently selected. |

For a request already completed by an early L1/Segment hit, a late shadow result cannot mutate the data
transaction. The invariant that both translations agree is guaranteed by install/revoke ordering; the
late result is checked by a retained audit token and a mismatch escalates to the same fatal error path.
This does not retroactively make an inconsistent mapping safe; it makes the violation observable.

## Descriptor update cost proxy

`C9_MODEL_DECISION`: selected `N=8` local state is `8*135=1,080` bits per cluster and
`35*1,080=37,800` descriptor bits per GPU. An install/revoke broadcast carries this state or an
equivalent versioned update to 35 destinations. This is a replication/update-bit proxy, not a wire,
latency, area or power estimate. Updates are outside active inference epochs, so v1 does not insert
an update conflict into nominal lookup timing; C10 still records update attempts, acknowledgement
latency and rejected lookup admissions for audit.

## Security and scope limits

- Only `READ` can Segment-hit. Store/atomic/execute semantics remain ordinary VM and must preserve
  exact-once request ownership.
- v1 has no descriptor replacement during an epoch, no dynamic priority and no indirect descriptor
  mapping. These are intentionally excluded, not accidentally free.
- Multi-model serving is supported only inside the one provisioned ASID when all active models'
  combined registered extent lists fit its eight descriptors and all local replicas. A simultaneous
  second ASID uses conventional paging. The driver reports descriptor count, coverage, pinning outcome
  and fallback reason per registration.
- A future implementation may add dynamic migration, larger/banked tables or a 2MiB segment class,
  but that requires a new architecture decision rather than widening v1 implicitly.
