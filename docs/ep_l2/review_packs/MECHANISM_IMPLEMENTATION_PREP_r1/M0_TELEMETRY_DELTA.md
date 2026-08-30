# M0 Telemetry Delta

All fields below are proposed, OFF by default, observation-only, and per L2 slice. They must not be read by admission/arbitration. Existing C7e exact preview and B0 accumulator are the implementation base.

## Required before M2

| parser field | production point | semantics / denominator | reset, scope, overlap |
|---|---|---|---|
| `m0_frontend_head_blocked_cycles.<reason>` | `memory_sub_partition::cache_cycle`, after exact `preview_access`, where `plan.exact && !admit` is already recorded (`l2cache.cc:1272-1300`) | increment once per cycle for the ICNT-L2 queue head when it needs that independently unavailable resource; reasons: tag-way, WAD-full, WAD-hazard, line-MSHR, descriptor, per-address, MissQ, payload-service, payload-capacity, lower queue, response queue. Denominator `m0_frontend_head_observed_cycles` increments once whenever exact preview is evaluated. | cumulative + 5K delta; one head/cycle. Multi-cause sets multiple reason fields, while `any_blocked` increments once. Never derive from retry events. |
| `m0_payload.resident_occupied/free` | frozen per-cycle sampling point `l2cache.cc:1023-63` / `ep_l2_b0_sample:1785-1830` | slots with role RESIDENT and `status!=FREE`; `1024-occupied` in static mode. | per slice, cumulative avg/max/hist and 5K windows; sample after drains/fills, before frontend admission. |
| `m0_payload.bypass_candidate_live` and `bypass_candidate_need` | **new semantic producer required at the chosen pending/bypass owner**, not the dormant store | live is count of admitted candidate transactions whose future fill/response needs temporary payload; need increments on a candidate allocation attempt. No field is emitted until the consumer contract is specified. | per slice/window; candidates must carry unique transaction IDs; do not use `m_ep_l2_payload.bypass_used()` as proxy. |
| `m0_payload.shared_shadow_grant/deny` | at the same candidate allocation decision, using a side-effect-free shadow allocator after real admission decision | shadow sees actual resident occupancy plus candidate bypass liveness and tests total 1152 capacity and chosen reserve; `grant` iff a real M2 allocation would be legal. Denominator `bypass_candidate_need` (and optionally resident candidate need). | no real allocation/ID/bank request; each candidate attempt once. Deny reasons: total-full, protected-reserve, no-consumer/unknown. |
| `m0_payload.role_complement_cycles` | per-cycle sampler | increment if one defined role has demand and the other has usable slack under the same policy; report directional `resident_can_borrow` and `bypass_can_borrow`, never an unqualified sum. | 5K/cumulative; two directions may overlap only if both definitions are true; parser retains both fields. |
| `m0_l2.useful_admit` / `useful_response_enqueue` | immediately after successful `l2_cache::access` / immediately before `commit_next_access` at `l2cache.cc:1065-1100` | count unique admitted frontend `mem_fetch` and responses actually accepted into L2→ICNT, respectively. | per slice/window. Exclude re-presented blocked heads; response count is not a request unique-ID surrogate without explicit UID dedup. |

## Existing fields that can be reused, not relabeled

`l2cache.cc:1181-1299` already has non-mutating exact preview and blocker inputs; `l2cache.cc:1796-1830` samples resident/bypass state; `l2cache.cc:2049-63` prints terminal resource evidence. Existing `payload_block`, `bank_block`, and retry/conflict fields remain event diagnostics. They are not cycle-based admission metrics. Existing bypass occupancy must be labelled `dormant_model_slots` until a production consumer exists.

## Later, separate telemetry

RO M3: per-request conservative eligibility reasons, MSHR lifetime from `add` to final `commit_next_access`, sector/descriptor occupancy, and write/atomic exclusions. TVD M4: dirty-victim selection, byte/sector mask, resident payload hold time from victim selection, WAD birth-to-`set_done` lifetime, and overlap with allocation denial. These are not required to choose M2 and must not delay its focused M0 patch.

## M0 equivalence gate

With the M0 switch OFF, representative workloads must match accepted baseline cycles and existing C7e/B0 counters exactly. With M0 ON, the controller paths, payload allocator, and outputs other than new observation fields must remain unchanged; a test should compare request/fill/response sequence and terminal leak checks.
