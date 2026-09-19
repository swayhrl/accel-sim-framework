# AWMA Current State

Date: 2026-09-19

## Coordination stage

`AWMA_Q05_GLOBAL_ACCESS_DETERMINISM_CLOSURE_174NEW_V1`

Node174-new remains the active scientific mainline.

Node109 is independently running the V2.1 ten-hour side campaign.

## Accepted lookup-stream identity closure

Execution:

```text
hrl/awma-q05-lookup-stream-identity-174new-v1
42f7c134ac9f2d1b0d789ba455a7cea76703ab56
```

Status:

`AWMA_Q05_LOOKUP_STREAM_IDENTITY_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Accepted facts:

- P34/P8 natural controls reproduce exactly;
- all rows have `post_ready_retranslation=0`;
- LOCAL and PARAM_LOCAL generated-access counts are invariant;
- the access-stream delta is entirely GLOBAL;
- aggregate GLOBAL dynamic memory instructions and active lanes are invariant;
- no architecture mechanism was evaluated.

P34:

```text
point      cycles   GLOBAL generated accesses
10/80      871835   549754
5/80       778598   551798
0/80       748102   637816
0/0        657110   644990
```

All P34 rows:

```text
GLOBAL dynamic_insts = 139776
GLOBAL active_lanes  = 4386816
LOCAL generated      = 226912
```

The previous stage classified:

`LOOKUP_STREAM_DELTA_EXPLAINED_BY_OTHER_ACCESS_GENERATION`

This is an intermediate classification only; the cause of GLOBAL access-generation variation remains unresolved.

## Important source audit after closeout

The previous telemetry counts unique access UIDs at the VM boundary, so the delta is not a simple retry double-count.

Accepted source also guarantees that after translation READY:

`mem_access_t::set_sim_pa()`

sets:

`m_vm_translation_applied=true`

so downstream cache/interconnect backpressure does not retranslate the same access object.

Trace-driven GLOBAL semantics are expected to be deterministic:

- trace parser provides active mask and lane addresses;
- `trace_warp_inst_t::parse_from_trace_struct()` copies them;
- GLOBAL addresses are not rewritten by `checkExecutionStatusAndUpdate()`;
- `generate_mem_accesses()` uses fixed coalescing rules.

Therefore the remaining GLOBAL access-count change is a simulator identity/determinism question that must close before mechanism work.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_GLOBAL_ACCESS_DETERMINISM_V1.md`

Primary goal:

> Join the same dynamic GLOBAL trace instructions across P34 10/80 and 0/80 by a timing-independent canonical trace identity and determine whether the difference enters before coalescing, inside coalescing/access generation, or after generation.

Canonical identity should derive from the trace:

```text
trace TB coordinates
+ trace warp id
+ trace instruction ordinal
```

not runtime `inst_uid`.

The stage first mines existing per-PC logs, then uses generation-time fingerprints and only the minimum 10/80 vs 0/80 rerun.

## Model-validity policy

Still frozen:

- L1/L2 10/80 = generic model assumptions;
- lookup timing is simulator-coupled;
- quantitative RTX4080 claims require native calibration;
- P34 = realism reference;
- P8 = screening-only.

## Node109 status

109 V2.1 side campaign remains independent.

It may collect `RECONNAISSANCE_ONLY` native TLB surfaces and workload assets.

174 must not consume unreviewed 109 results during this determinism stage.

## STOP boundary

If a simulator correctness defect is proven and fixing it would change accepted Q05 scientific results, STOP_FOR_SCIENTIFIC_REVIEW.

Do not silently repair the scientific baseline.

No TLB/PTW/cache mechanism starts automatically.
