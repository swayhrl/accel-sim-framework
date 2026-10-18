# Final CPU qualification matrix

**SCIENTIFIC_STOP for compact implementation. PASS only for parent regression,
production capacity witnesses and test-local resource assertions.** Final source
Core835417b37627e46eaaf215f3ff697263c94a18cc; executed Framework tools
2a08aee8a5290603c83a0b4f805569762e5ab191. All final builds/asserts/load paths
are bound in SHA_BINDING.json. Build concurrency never exceeded2; own new CPU
work only, no reuse of old AC CPU allowance/products. Final rounds are in
/workspace/dtc-lane-ac2-compact-collect-174-v1/final-cpu/.

| Test | Final result | Scope |
|---|---|---|
| AC2 original7 + AC resource + AC2 bound CTest |9/9|parent regressions and new resource evidence; no compact integration test |
| Fresh immutable parent AC CTests |8/8|independent rebuild of83aca449 |
| Fresh immutable X2 CTests |7/7|independent rebuild ofe32afdcf |
| Parent CPU matrix rerun with new products |80 processes:75 positive,5 expected unsupported ON rejections|real production LDST/RFU/normal print; same original17 cases |
| All-OFF versus X2 |17 state triples,51 public normal boundaries identical|omitted and0; only host-rate line excluded |
| Existing AC ON versus new AC2 ON |17 paired cases,51 normal boundaries identical|parent AC160KiB semantics preserved exactly |
| New source-coalesced boundaries |4/8/16/128/129/256/257/512 sectors, each across5 arms|AC2 OFF/ON, parent OFF/ON, X2 omitted;40 positive CPU processes |
| Manual full640-line pool |2560 sectors,5 comparison arms|all640 refs admitted, actual lower640 roots/returns and final drain; structural input, not ISA witness |
| New boundary equivalence |9 OFF/X2 and9 ON/parent cases,27 normal boundaries per relation|actual source coalescer except explicitly manual fullpool |
| Exact4KiB single bank / both banks occupied |128 sectors fits, two full banks hold on denied WB then drain|test-local original bank-owner object, NOT production compact mode |
| Capacity negatives |129 against128,257 and512 against256 hard-assert|3 forked SIGABRT children; plus original AC resource6 assert negatives |
| Unavailable compact parser |compact1 rejected, exit1 Unknown Option|no silent legacy/compact substitution |
| Normal64-SM cumulative parsing |complete64 unique rows, no-event sentinel and last whole snapshot|existing AC normal output, not a new compact summary |
| Malformed export |16 required parser negatives rejected|missing/duplicate/truncated/invalid data; no old-frame fallback |

The original17 cases include multicycle4/8/16-sector collection, same-ready pairs,
actual RFU bank denial and later retry, ordinary WB arbitration, same-warp fence,
completed fence priority, partial admission, late waiter wakeups, K1 retained
Refs, actual old-generation lower request already inflight before map loss, and
noncacheable sidecar observations that do not repeat architectural completion.
Three same-cycle LDST microsteps cannot replenish finite quotas. New capacity
cases likewise use three microsteps, preserve original4-sector/1-retire quotas,
K1 source requests while old physical data/returns may remain live, and conserve
Refs/credits/PIB/physical/registered-vs-closed completion dependencies at checked
edges and final drain.512-sector API input yields256 fully admitted references;
manual fullpool yields640. No mask/data truncation is used to make either finish.

The final qualification runner made88 top-level subprocess calls, including
build-only probe compilation, CTest/parent-matrix aggregations and negatives;
that count must not be presented as88 independent compact tests. Structured
CPU_TEST_RECEIPTS.json preserves exact arguments, result scopes, raw paths/hashes,
actual library maps and all equivalence/negative receipts.

## Explicit limits and tests not implemented

Compact overflow fallback, compact LDST stage/diagnostic integration and compact
finite-progress PASS are **NOT IMPLEMENTED_SCIENTIFIC_STOP**. The9/9 result must
not be called compact9/9 integration PASS. Small-bank tests exercise an original
header object with test-local capacity injection; all production LDST capacity
runs use unchanged AC80KiB banks or original X2 serial timing. Their successful
drain is not evidence that an8KiB fallback drains. source_API reachability is
not an executed ISA/trace legality/value proof. Fullpool pre-coalesced metadata is
explicitly synthetic. The reused fixture has controlled CPU lower packets,
admission setup and unused/no-DRAM-cycle n_ref=0 in all comparison arms.
No DRAM/ICNT/GPU simulator cycle(), kernel, trace, native application or simulation
thread runs. No loaded values, byte extraction/routing, full ISA/coherence or PPA
are verified. No compact performance or false-acceleration claim is made.

## Preserved engineering diagnostics

Initial CTest failed to load the matching libcudart because of inherited loader
state. A test-only CTest ENVIRONMENT pins its own library; every final positive
probe binds actual dladdr, /proc/self/exe and maps. Five inherited expected aborts
lack flushed runtime maps and are not positive-load witnesses. An incremental
candidate exposed a stale embedded build string; final qualification uses a new
empty build directory at immutable835417b3. An initial fullpool3000-edge budget
ended while collection was still progressing (640 refs held,812 sectors left);
the final test derives max_steps=8*references+ceil(sectors/4)+32. This changes only
test work budget; no production assertion/quota is relaxed. A superseded rebuild
was stopped before final immutable-source build. All prior logs/products remain
in the own raw/build paths and are excluded from final PASS receipts.
