# Track C: Main review addendum (ASCII)

This addendum restates the sealed hardware_delta_v1 delivery in ASCII because the original Chinese entry was damaged by the PowerShell pipe encoding. The original ten files and their manifest are preserved. No test is rerun for this documentation-only addendum.

## What was implemented and checked

quota_commit_contract.py is an independent functional transaction contract. It does not modify or execute production bf4, its ELF, a native entry, a Trace or a scientific model.

The new CPU receipt reports PASS for 12 directed case groups and 3,185 exhaustive two-row state/operation combinations. Existing bf4 production CPU/parser tests and their receipts were reused without rerun. These checks establish bounded arithmetic and transaction behavior only. They do not qualify production integration, hardware timing, PPA or application performance.

## Concrete port, timing and net-delta contract

The selected proposal explicitly provisions K=2 directory-row service lanes and one clean-count commit lane per slice. A K=1 comparison is supported. Existing source output reporting three indexed update lanes is not evidence of a free quota-update port.

A batch uses a READ beat followed by a nonoverlapped COMMIT beat. No new batch starts while a prepared batch is pending. At best, a full K=2 batch serves two row transitions in two contract cycles. A downstream hold charges another contract cycle on each attempted waiting beat. These cycle counts are chosen scheduling rules, not measurements of a real hardware clock.

Every row transition consumes row service, including zero-count-delta WB acceptance/completion and read-lease changes. Same-row collisions defer the second operation. More than two submitted candidates causes a port-bound refusal. No implicit extra row lane or speculative visible mutation is provided.

For each accepted transition:

    delta_i = isCLEAN(new_state) - isCLEAN(old_state)

Each delta is -1, 0 or +1. Two inputs require a signed three-bit sum for the range -2 through +2. Logical count and cap each require eight bits for values 0 through 128. A signed nine-bit projected intermediate covers -2 through 130. These are logical minima, not synthesized area.

CLEAN-to-CLEAN replacement folds the original decrement/increment into one net-zero transition. Two distinct-row -1/+1 transitions can publish atomically with one count write. Admission checks the count after each accepted transition in input order. A later decrement does not rescue an earlier quota-blocked increment; this deliberately incurs a retry bubble without lookahead reorder.

Example checks:

- Count63/cap64 with two attempted increments admits one and blocks the other.
- A full-cap CLEAN replacement has one row write and one net-zero count write.
- Reclaim -1 followed by install +1 can commit both rows atomically in two contract cycles.
- At full cap, install +1 before reclaim -1 requires a later batch for the blocked install, totaling four contract cycles.
- Three downstream hold beats preserve all visible row/count/ack state; READ1 + hold3 + COMMIT1 totals five contract cycles.
- Cleanup of 128 CLEAN rows costs 64 batches / 128 contract cycles at K=2, or 128 batches / 256 cycles at K=1. It is not a free same-now loop.

All refusal checks precede visible mutation. Row incarnation, payload generation, global revision, pin and resource-reservation conditions are checked. COMMIT checks the prepared snapshot again and publishes all accepted row transitions, count target, revision increment and acknowledgements together. The new batch interface uses one shared base revision; bf4 originally checks individual plans. Equivalence of batching to production ordering is not established.

Six logical producer heads are attempted round-robin: WB completion, lower-WB acceptance, frontend install/reclaim/promotion, read-lease begin, response/cancel retirement, and cleanup. At K=2, six continuously presented heads are each attempted within three READ beats, excluding pending/downstream waits. This proves attempt fairness only, not unconditional progress.

Additional costs include two pending operation/row records, old/new row snapshots, base revision, projected count, signed delta and handshake flags. A proposed completion ingress depth of two per slice is a costed design item awaiting capacity and clock-domain qualification. The CPU arbiter references heads; it does not prove existing production queues can retain every event. Exact RTL packing, gate delay, power and area remain unknown.

## Real production integration cut points

1. gpu-cache.cc:1638-1639 pushes to m_memport before lower_accepted changes the WB row. Counter/row service must be reserved before the packet leaves its original head. Actual lower enqueue, row transition and payload ownership transfer must commit together. Stalling only after the push is too late.

2. l2cache.cc:858-869 returns arbitration credit before calling the subpartition set_done. set_done is void, and callers may delete the packet after the callback. A completion must remain at its real origin or in a qualified bounded ingress until COMMIT acknowledgement. Return-credit, tracker erase and deletion must wait for that acknowledgement. UID, row incarnation and payload generation must stay bound; the completion CAM path remains separately charged.

3. Missing-sector reclaim can fall through into ordinary frontend work. Landing reclaim, retention and promotion can cause further row mutations. Real tag, allocator, MSHR and lower resources must be reserved before destructive mutation. More than two required rows must HOLD unless a separately qualified multi-beat atomic group is implemented. The actual reachable maximum number of row intents is not yet proved.

4. Read-lease begin must commit lifetime protection before a bank request. Response retirement must bind exactly once to actual enqueue. The standalone readers field is not a qualification of production payload pins, sector/version data, bank scoreboard or ICNT atomics.

5. Production epoch cleanup uses a while-reclaim loop at one supplied now. A hardware implementation must schedule row service and finish allocator releases before acknowledging drain, charging the resulting cycles.

SOURCE_HANDSHAKE_CUTPOINT_EVIDENCE.txt contains exact source snippets and hashes. SOURCE_TO_HANDSHAKE_IMPLEMENTATION_TABLE.json maps required changes and remaining gaps. No Core862 clock-domain repair is merged or inherited.

## What remains unqualified

There is no production adapter, RTL integration, real port arbitration, faithful production cycle implementation, synthesis, clock closure or PPA result. Producer bounds, same-row collision policy, grouped snapshot ordering, pre-push/pre-credit handshake, credit conservation, bounded completion ingress/CDC, full payload/sector/version semantics, allocator uniqueness, generation exhaustion and rollback integration remain work for a future reviewed implementation.

Any production implementation of this timing contract creates a NEW Source5/ELF identity and needs fresh qualification and a sameSource baseline. It cannot be relabeled bf4/bab27c or paired with bf4 results as if the Source were unchanged.

## Separate bf4 reference request remains unauthorized

BF4_SAME_SOURCE_REFERENCE_REQUEST_PROPOSAL.json proposes one FUTURE independent FWT cap128 reference start using unchanged bf4/bab27c and the existing exact 283-option candidate. Current requested execution starts, authorization, scientific budget registration and native consume are all zero. The user's A1/B/A3 six-point approval does not authorize Track C.

No accepted bf4 performance control is present in the reviewed accepted small summaries. Historical Source78 or Core862 cycles cannot be denominators. Later bf4 cap64/0 points require separate approval and must match the same input, config, observer and geometry except quota. Results from a future new hardware Source cannot be called sameSource with bf4.

The current candidate uses B0/M0a/MS111. Application observer NI is unresolved, and no NI starts are included. Main must close formal Host/native mapper, source/mode/input/observer, actual resource admission and archive/restore qualification before seeking explicit Track C authorization and registering an exact fresh one-start budget with native consume before fork.

The proposed FWT reference resource envelope is RSS3GiB, AS12GiB, wall3600s and result128MiB. It is a proposal based on historical scheduling evidence, not a new bf4 measurement. An unchanged bf4 reference would characterize its current algorithmic implementation with quota-update timing still unmodeled; it cannot prove this new hardware design physically feasible.

All work in this delivery started zero scientific models, created zero Trace, registered zero scientific budget, performed zero native consume, and changed no production source/ELF, historical evidence, shared route or executor.
