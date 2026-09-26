# Source feasibility

Evidence labels: source claims below are `VERIFIED_CODE` at frozen source
authority `2bbbceabb5261777fe385289ecb6579791e0f232` unless stated otherwise.

## Event separation

| Event | Frozen source point | Meaning |
|---|---|---|
| resident request visible | `ldst_unit::memory_cycle`, `inst.accessq_entries()` | Access exists in the dynamic instruction queue; it need not be the consuming head. |
| request/head ready | `inst.accessq_back()` before `translate()` | This exact access currently demands translation in the normal consumption path. |
| physical lookup launch | `translation_controller::translate`, accepted L1 port | Real L1-TLB service begins; retries denied by the port are not launches. |
| translation result ready | controller `LOOKUP_READY` / PTW completion | A physical translation outcome exists; it is not yet necessarily applied to the access. |
| result applied | `apply_ready_translation` or head-path `set_sim_pa` | SimPA and translation outcome are attached exactly once. |
| cache admission | `process_memory_access_queue_l1cache` and L1 latency/bypass paths | Data-port, bank, reservation, or interconnect conditions can still delay the translated access. |

These events must not be collapsed into one “ready” timestamp.

## Existing ordering relevant to H2

With pipelined accessq translation enabled, `memory_cycle` scans resident
entries and calls the translation controller before binding
`mem_access_t &access = inst.accessq_back()` for the head path. The controller
enforces the configured finite L1-TLB port. Therefore a same-cycle ordering
question is source-feasible to observe without a trace oracle.

The later L1D path separately checks `data_port_free`, the target bank's
latency slot, cache reservation status, or interconnect capacity. Translation
completion does not imply cache admission.

## State available without an oracle

- current dynamic instruction object and resident accessq order;
- per-access UID within a run;
- exact current translation identity and generation;
- current applied/ready state;
- controller port grant/denial and physical launch;
- current cache/interconnect admission outcome.

Cross-run request-set comparison must not use `(sid << 32) | inst.uid` as a
stable identity. Lane B must bind a trace-stable dynamic instruction/request
identity (kernel/CTA/warp occurrence/instruction occurrence/address-sector-
lane provenance) in its committed handoff.

## Missing state and interpretation limits

- `Scoreboard::checkCollision` exposes register collision, while
  `pendingWrites` exposes only whether a warp has pending writes. They do not
  identify whether the producer is memory, compute, or translation-delayed.
  Translation-specific warp-progress attribution therefore needs an explicit
  mapping rather than relabeling generic scoreboard counts.
- Existing aggregate Observatory counters and 512-cycle windows do not expose
  the exact H1 last-group condition or H2 same-cycle port collision.
- A1 and A2 are separate single-kernel simulator replays with freshly created
  simulator state. Their captured producer contexts differ, but the simulator
  does not replay the complete preceding model execution. “Context/history” is
  therefore a trace-origin distinction, not proof of modeled warm history.

## Minimal observer fields if Lane B justifies continuation

Per event, bounded to selected targets/windows:

`cycle, sid, kernel_identity, stable_instruction_identity, access_uid,
group_identity, accessq_position, group_count, unresolved_group_count,
baseline_eligible, port_granted, physical_launch, translation_ready,
address_applied, cache_admitted, cache_failure_class`.

The observer must be separable from functionality, default OFF, and neutral in
cycles/service when enabled. It must not allocate an unbounded global history
in a full-kernel performance run.

## Prototype feasibility

- H1 predicate: feasible once Lane B exposes finite live-instruction group
  state and a stable mapping. The current source does not already maintain the
  exact last-unresolved flag at the arbitration point.
- H2 predicate: directly feasible at the existing resident-scan/head boundary;
  a matched implementation must preserve existing port count, eligibility,
  work conservation, already-issued requests, and fallback.
- Neither hypothesis needs a new capture, model download, RTL, or PPA study.
