# AWMA Current State

Date: 2026-09-19

## Coordination stage

`AWMA_Q05_LOOKUP_STREAM_IDENTITY_CLOSURE_174NEW_V1`

Node174-new remains the active scientific mainline.

Node109 is executing the independent V2.1 10-hour side campaign under its own GPU-lock wait/active-window policy.

## Accepted lookup-model validity closure

Execution:

```text
hrl/awma-q05-lookup-model-validity-174new-v1
9bbfad6ce1add1a6292f8177de7d92e71a3572d4
```

Status:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Key accepted conclusions:

- L1/L2 lookup latencies 10/80 are `GENERIC_MODEL_ASSUMPTION`, not RTX4080/Ada hardware calibration;
- read-only fill-race telemetry is neutral;
- all bounded points have `LAUNCH_MISS -> COMPLETE_HIT = 0`;
- previous lookup-stream variation is not explained by fill-during-service residency races;
- result classification:
  `LOOKUP_TIMING_COUPLED_NEEDS_MODEL_CALIBRATION`;
- no architecture mechanism was evaluated.

## Accepted invocation evidence

P34:

```text
point    cycles    lookup launches
10/80    871835    776915
 5/80    778598    779016
 0/80    748102    865036
 0/0     657110    872241
```

Q05 instruction/CTA totals remain unchanged.

`vm_requests` is retry/function-invocation telemetry, not unique translation work.

At natural P34:

```text
vm_requests                     9,254,048
lookup admissions/completions     776,915
inflight bypass invocations      7,266,036
pending waiter bypass              434,431
```

Lower lookup latency sharply reduces retry/inflight invocation counts but increases the number of completed lookup requesters/accesses.

The cause of the latter increase remains unresolved.

## Source fact: no post-READY retranslation of one mem_access_t

Accepted source:

`ldst_unit::memory_cycle()`

only enters translation when:

`!access.vm_translation_applied()`

and on READY:

`access.set_sim_pa(...)`

sets:

`m_vm_translation_applied = true`

Therefore downstream cache/interconnect backpressure does not cause the same `mem_access_t` to re-enter translation after READY.

This removes one possible explanation for the changing lookup count.

## Current hypothesis to test, not accepted conclusion

Global/local/param-local instructions create `mem_access_t` objects during access generation/coalescing.

Local-memory timing addresses are mapped by:

`shader_core_ctx::translate_local_memaddr()`

using runtime SM/CTA/thread placement before coalescing.

Therefore translation timing may indirectly change CTA/SM execution placement/order and thus local-memory coalescing/access-object identity.

Q05 has substantial local-memory activity, so this is worth testing.

No claim is made until per-space/per-PC/per-SM conservation closes.

## Active mainline

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_LOOKUP_STREAM_IDENTITY_V1.md`

Goal:

- prove access UID translation invariants;
- add read-only per-space/per-PC/per-SM access-generation telemetry;
- compare P34 10/80, 5/80, 0/80, 0/0 and a minimal P8 pair;
- attribute lookup-count changes to generated access-object identity;
- optionally use an existing source-safe fixed-placement diagnostic if and only if needed.

No architecture mechanism.

## Same-trace/baseline policy

- P34 = final realism reference;
- P8 = screening prefix;
- formal isolated member34 = same-trace isolated control;
- historical standalone isolated remains cross-capture evidence only.

## Native calibration status

Formal RTX4080 lookup calibration is still absent.

Node109 V2.1 is allowed to collect `RECONNAISSANCE_ONLY` native TLB surfaces, not to overwrite simulator 10/80.

174 should not use unreviewed 109 recon output during this stage.

## STOP boundary

After lookup-stream identity closure, STOP for ChatGPT review.

Do not begin a TLB/PTW/cache architecture mechanism automatically.
