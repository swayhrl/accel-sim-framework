# CPU test matrix and limits

Released Core: **83aca449135703c176cfab29ae43e1245d00a557**.
Qualification tools source: Framework **ab1930efc4135f0d6a4fcc4b81f48303bc4b87a4**;
later review commits do not replace this execution-source identity.

**PASS_CPU_REAL_LDST_PIPELINE_SCOPE_ONLY**:80 processes =75 successful positive
processes +5 expected unsupported-ON configuration rejections. Original7 Core
CTest sources are unchanged and all7 pass; one new bounded-resource CTest also
passes, including6 deliberate hard-assert negatives. This is a real production
LDST/RFU/ledger component qualification, not a simplified reference scheduler.
Full GPU/ISA/value/real-network integration remains **PARTIAL / UNTESTED**.

Each17-case row below runs against freshly built immutable X2 and new Core
{omitted, explicit0, explicit1}. All17 OFF triples have byte-identical typed
per-edge state, and51 corresponding normal-print boundaries have identical
old public output after excluding only the host wall-time `gpu_total_sim_rate`.
Initial/terminal/later-terminal prints use actual `gpu_print_stat()`, not private
observer/stage printers. Normal printing leaves original observer/stage bytes
and the clock unchanged.

| Case | Bounded production witness |
| --- | --- |
| pair4 /8 /16 sectors per instruction | Same ready edge for both; original strictly later collection/WB; successful WB and other-owner collection overlap; no4-sector or1-retire quota violation |
| single4 /16 | ON/OFF typed state and timing identical in this isolated fixture |
| empty | ON/OFF state identical; true empty/no-sample64-SM snapshots are also parsed |
| denied4 /16 | Actual RFU bank reservation denies WB; slot/data/Refs held; three LDST invocations per absolute cycle; retries on later cycle, eventual drain |
| arbitration4 | Controlled phase1 WB copy held by real RFU denial; actual LDST arbiter skips DTC WB, independent ON collector still advances; test copy clears only after verifying no completion |
| fence | Incomplete older same-warp PROXY_FENCE prevents younger collection while another warp progresses; original source completion unblocks it |
| same_warp | Completed fence between two same-warp loads preserves blocking and sidecar priority; no extra architectural effect |
| partial8 /16 | Frontend can already be ready for admitted subset; incomplete full-reference admission still forbids collection; actual dispatch then completes through LDST cycle |
| late_waiter | Twelve existing consumers, four-waiter finite wakeup edges, a thirteenth waiter attaches while drain is pending; one real lower root, four controlled32B return packets, exact refs/wakeup/ledger drain |
| generation+K1 | Real lower root is created/inflight/credit-owned BEFORE mapping loss. New same-address physical allocation identity coexists with old identity, old packets still reach old owner; both drain |
| K1_refs8 | Lookup loss before collection and while denied result/collector owners live; repeated source requests preserve refs until successful WB, final physical reclaim conserved |
| sidecars | Store/atomic/bypass/fence observations consume no data bank and add no architecture instruction completion; original source completion count equals observation retirement count |

Controlled pair timestamps illustrate the component change; they are not measured
GPU application performance:

| sectors/instruction | OFF first/last WB | ON first/last WB |
| --- | --- | --- |
|4|15 /17|15 /16|
|8|20 /23|20 /22|
|16|30 /35|30 /34|

All80 processes pin exact probe/library/config/source identities. Actual
`dladdr`, executable identity and library `/proc/self/maps` are retained for75
positive processes. Five expected aborts did not flush their startup stdout;
their configured library/hash and rejection stderr are recorded, but they are
**not** claimed as runtime-map witnesses. Binary hashes are checked before/after.

Additional normal-path cases cover full64-SM K1+pipeline, ON empty64 and OFF
empty64. Exactly64 unique rows per frame, no-sample sentinels, and last-whole-frame
selection pass. Sixteen parser corruptions are rejected: missing/duplicate SM,
truncated final frame/row, missing/duplicate/oversized field, sentinel, sector
conservation, data capacity, per-cycle quota, private/unframed, missing export,
version mismatch, missing final newline and unexpected OFF export. Earlier valid
frames never license fallback from a broken final frame. ON mode0/1/2/4 with
finite1 and OO+finite0 all fail closed; OFF initialization in other modes passes.

Each CPU edge checks shadow Ref conservation, physical identity, lower credits,
max4 sector reads and max1 retire; final checks close all registered completion
dependencies and lower create/issue/return counts. Normal service decomposition
remains ready-to-complete = ready-to-collect + collection cycles + WB wait.
Resource CTest fills both full80KiB banks and asserts the160KiB total bound, slot
ownership, denied-slot hold, later-cycle retry, histogram repair for a later same-
cycle WB, double-owner/overcapacity/over-port/double-retire/double-attempt rejection,
and the unchanged hard stale-physical-generation assertion.

## Test seams and preserved engineering failures

The fixture invokes real issue/admission helpers between selected edges to align
inputs, then actual LDST cycle(), WB arbitration, RFU bank grants and ledger
completion. Lower packets are produced by a CPU link; ICNT/L2/DRAM are not clocked.
Synthetic warp metadata enters real issue()/LDST helpers; no GPU kernel or
native application is launched, no ISA execution or trace replay occurs, and
GPU cycle() is never called. Store/atomic/
bypass sidecar observations do not execute their full architectural value paths.
This supports bounded timing/ownership results, not a complete value/coherence/
ISA proof or full-simulator performance claim.

The initial1-channel CPU fixture failed Volta IPOLY address hashing in return
cases. It was corrected to the source profile's32 channels/2subpartitions, without
changing production hashing or the memory system. The first strict OFF public
comparison exposed unchanged baseline `dram_t::n_ref` being uninitialized. Both
CPU fixtures now explicitly initialize the unused/no-cycle refresh input to0;
no production DRAM repair or relaxed comparison was made. This limits the
well-defined CPU equivalence domain, and does not prove natural full-run DRAM
initialization. Only the host-rate line is excluded from successful comparisons.
Earlier failed logs and superseded qualification candidates remain in the own AC
raw root; none are promoted to final83aca449 evidence.
