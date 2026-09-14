# Route B tracer capability audit

## Current evidence

The retry570 targeted-memory tool at G commit
`b879d2b83b1b00acbb69c1d49960162a48045117` does exact full-mangled function
matching, emits a complete NVBit static map, and rejects a target unless it is
direct `GLOBAL`, `LDG`/`STG`/`ATOM`, and has an MREF operand. This is sound
single-static-index discovery evidence.

It cannot capture Route B as specified: it accepts one
`C16_NVBIT_TARGET_INSTR_INDEX`, allocates one `TargetRecord`, retains only the
first nonzero address, and does not serialize every event, active/predicate
mask, width, or every active lane. It is therefore not a multi-GLOBAL-MREF
Route B producer.

The existing maps make the delta concrete: any formal LargeIndex capture must
whitelist 34/101/130 and any formal SmallIndex capture must whitelist 17/85/104,
subject to map-SHA revalidation at runtime. The old Route-A ban on using 34 as
a chosen single-PC target does not authorize omitting it from an exhaustive
Route-B map predicate.

The frozen full tracer can restrict dynamic kernel ranges/name regexes and can
serialize masks, predicate masks, widths, and addresses. Its instrumentation
loop nevertheless inserts callbacks for every instruction in the selected
interval (including non-memory records) and traverses related functions. It has
no committed exact-function plus `GLOBAL && has_mref` whitelist, so a wide
interval can emit a prohibitively large trace and admits no proof that only the
desired rows were emitted.

## Minimum future delta

Extend the targeted tool—not its current diagnostic record—with a map-SHA
checked, exact-function, sorted static-index whitelist. For each whitelist
GLOBAL-MREF instruction, emit an append-only bounded event record containing
the Route B schema fields and a terminal record; carry MREF ordinal and reject
unsupported multi-MREF handling rather than silently choosing operand zero.
The host must enforce an output cap, record drop/overflow status, and fail
closed before writing a formal manifest. This delta requires a versioned tool
binary, paired small qualification, parser fixture, and SHA-bound canary.

## Memory-only observer

Decision remains **NO_GO**. No new paired real-GPU equivalence, terminal, size,
or perturbation evidence exists. `REOPEN_FOR_BOUNDED_CANARY` is only a future
option after those exact evidence requirements pass; Route B's present safe
fallback is the qualified full tracer where its bounded scope is acceptable,
not an unqualified memory-only observer.
