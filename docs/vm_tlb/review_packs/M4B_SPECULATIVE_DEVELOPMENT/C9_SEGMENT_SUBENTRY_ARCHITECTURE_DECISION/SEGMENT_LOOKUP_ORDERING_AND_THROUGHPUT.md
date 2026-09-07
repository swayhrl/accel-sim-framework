# Segment + L1 lookup ordering, throughput and latency

## Chosen policy: `HIT_FIRST / MISS_JOIN`

`PAPER_SPEC`: L1 and Segment lookup may be parallel, and a Segment hit masks/discards conventional
paging. `EXISTING_MODEL_FACT`: frozen C3 waits for both completions, so an L1 hit is unnecessarily
visible only after a slow Segment. `C9_MODEL_DECISION` replaces that policy with the rules below.

### Admission

At a translation cluster's one-request-per-cycle L1 admission point, one join token is allocated and
both requests launch in the same cycle:

```
token = {uid, asid, va, bytes, access, issue_epoch, owner=PENDING,
         l1={PENDING}, segment={PENDING}, l2_not_issued=true}
```

The local Segment table accepts exactly one lookup/cycle, matching the C4 local L1 port. Thus nominal
`segment_queue_delay=0`. A future topology with less throughput must explicitly enqueue before
admission or backpressure the L1 admission; it may not silently serially delay the Segment path.

### Completion transition table

| First observable condition | Required action | Lower translation action |
| --- | --- | --- |
| Segment **hit** before L1 | validate PA/permission/epoch; set `owner=SEGMENT`; complete immediately | cancel/guard any unissued L2; late L1 result is shadow-only. |
| L1 **hit** before Segment | set `owner=L1`; complete immediately | no L2; late Segment result is shadow-only and must agree if it is a hit. |
| L1 **miss**, Segment pending | retain token; do not issue L2 | `MISS_JOIN`: wait for Segment. |
| Segment **miss**, L1 pending | retain token; do not issue L2 | `MISS_JOIN`: wait for L1. |
| both miss | issue L2 exactly once | ordinary L2/MSHR/PWQ/walker/PWC/PTE path only now becomes legal. |
| L1 and Segment hit same cycle | verify PA and effective permission; choose `owner=SEGMENT` for attribution | no L2 or conventional fill due to Segment-hit precedence. |
| late hit after owner is set | compare retained mapping/permission audit fields; record discard | no second completion, fill, L2 launch or data side effect. |
| mapping/permission/epoch mismatch | raise `SEGMENT_L1_CONSISTENCY_FAULT`; stop uncompleted request and quiesce/error policy | no heuristic winner; never send conflicting mapping onward. |

An L1 hit is never delayed by a slower Segment result. An L1 miss cannot launch L2 while a valid
Segment result could still arrive. A Segment miss cannot cause an L1 reprobe. Each join token has
exactly one owner and exactly one terminal completion.

## Timeline examples

```
L1 hit first:       t0 launch both -> tL1 L1 hit / complete -> tSeg late result discarded+checked
Segment hit first:  t0 launch both -> tSeg hit / complete -> tL1 late result discarded+checked
L1 miss first:      t0 launch both -> tL1 miss / join -> tSeg hit complete OR miss -> L2 launch
Segment miss first: t0 launch both -> tSeg miss / join -> tL1 hit complete OR miss -> L2 launch
```

The C3 raw/effective L1 accounting remains historical evidence, but C10 must replace its wait-both
meaning with owner/early-completion fields. C4's exact-once frontend hash remains a regression
invariant, not post-C10 performance evidence.

## Throughput and queue contract

| Item | v1 contract | Label |
| --- | --- | --- |
| placement | one table local to each translation/L1 cluster | `C9_MODEL_DECISION` |
| descriptor capacity | 8 total descriptors for one provisioned ASID per local table | `C9_MODEL_DECISION` |
| request accept rate | 1 Segment lookup/cycle/local cluster | `C9_MODEL_DECISION` |
| aggregate nominal ingress | 35 lookups/cycle across 35 clusters | `EXISTING_MODEL_FACT` + `C9_MODEL_DECISION` |
| normal queue | no separate Segment queue; lockstep admission with L1 | `C9_MODEL_DECISION` |
| install/revoke conflict | driver changes tables outside active epoch after quiesce | `C9_MODEL_DECISION` |
| future insufficiency | explicit queue, backpressure and stall telemetry required | `USER_APPROVED_DIRECTION` |

One lookup/cycle is a throughput, not a one-cycle latency, promise. It applies to all translation
requests at the local admission point. The trusted table itself determines range match, so no
`OBJECT_WEIGHT` preclassifier exists. Misses do not consume L2 until both L1 and Segment miss.

## Latency model and sensitivity

`C9_MODEL_DECISION` decomposes service conceptually as:

```
Lseg = L_range_compare + L_asid_epoch_permission + L_pa_add + L_local_route
Tsegment_response = issue + Qsegment + Lseg
```

For v1 lockstep local admission, `Qsegment=0` by contract. `Lseg` is a configuration parameter.
`10` is retained only as the nominal reproduction point inherited from C3. Required model points are:

| point | `Lseg` | interpretation |
| --- | ---: | --- |
| fast sensitivity | 5 cycles | parameter sensitivity, not a process claim. |
| nominal | 10 cycles | compatibility/reproduction point only. |
| slow sensitivity | 20 cycles | tests L1 early completion and correct miss join. |

No result may call 5/10/20 a measured hardware latency. If C10 adds banking, shared arbitration,
more than one local ingress, or dynamic updates, it must add `Qsegment` and report queue occupancy,
queue wait cycles, port denials and admission backpressure. It cannot keep v1's zero-queue assumption.

## Required future telemetry

`USER_APPROVED_DIRECTION`: miss-rate-only reporting is insufficient. C10 must export, globally and
per kernel, at least:

- Segment accepts, port denials, queue high-watermark, queue wait cycles and backpressure cycles;
- `Lseg` configured value and decomposition fields; local table capacity/loaded descriptor count;
- join transitions: L1-first hit, Segment-first hit, L1-first miss join, Segment-first miss join,
  both miss, same-cycle dual hit, late discard and consistency fault;
- owner-selected completion count, lower launches suppressed before L2, and proof
  `accepted = exactly_one_terminal_owner + explicitly_cancelled/error`;
- L1/L2/PWC/MSHR/PWQ/walker/PTE wait/stall and service intervals, not only hit/miss counts;
- data/store/atomic frontend exact-once hash or equivalent side-effect conservation.

The state machine must also export whether an L1 hit completed before Segment. This separates a
measured cycle change from a new queue/latency artifact.
