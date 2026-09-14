# Route B GPU execution handoff

`STATUS=PREPARED_NOT_AUTHORIZED_TO_RUN`

Do not run this document unless the user/ChatGPT gives a new explicit GPU
authorization. It is a handoff plan, not authorization.

1. Bind the authority inputs in `LLAMA_S0_KERNEL_CENSUS_INPUT.tsv`. Refuse a
   scenario, model revision, runtime, input, code-object, or receipt mismatch.
   Do not reuse G1 S1/S2 catalog rows for S0.
2. Obtain a phase-linked native S0/B1/T128/Decode4 kernel census using the
   frozen workload. Preserve its manifest/SHA and rank it strictly with
   `ROUTE_B_KERNEL_SELECTION_RULES.md`. Current selected count is zero; the
   anchor rows are not authorization to bypass this step.
3. For each selected exact full-mangled function, run map-only discovery,
   retain the static-map SHA, filter all and only `GLOBAL && has_mref=1` rows,
   and classify load/store/atomic. Freeze the sorted index list before tracing.
4. Build/use a versioned Route B producer that meets `ROUTE_B_TRACE_SCHEMA.md`.
   The current targeted-memory tool is single-record diagnostic only and is not
   sufficient. Qualify the minimal delta with a paired fixture first.
5. Compute the storage budget before arming. Enforce <=4GiB and <=20 minutes
   per window. Use deterministic static-index partitioning if needed; retain
   group hashes and a union/no-overlap receipt.
6. Run the bounded canary and require every condition in
   `ROUTE_B_CANARY_ACCEPTANCE.md`. Stop on identity/map/terminal/checksum/mask/
   space failure, zero GLOBAL rows, overflow, size/time overrun, or unexpected
   dynamic-record growth.
7. Only after canary PASS, run formal partitions. Copy raw files without
   deleting sources, then verify source and destination SHA256 and size,
   publish receipts/manifests/static maps/checksums/terminal status, and leave
   raw payloads outside Git.
8. Scientific wording: results cover all direct explicit GLOBAL-MREF
   instructions in the named representative kernel and declared partitions.
   They do not characterize the model or phase as a whole, physical mappings,
   TLB/cache events, or global temporal reuse. Route C is separately required
   for a phase-coverage statement.
