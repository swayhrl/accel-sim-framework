# E2 conditional L1 miss-queue decision

Status: PREPARED_NOT_REGISTERED_NOT_STARTED. E1 DRAM935 must run first. This note prepares a conditional second execution; it does not spend or extend scientific budget.

## Exact scope

The finite goal permits E1 once, then at most one conditional E2. No baseline rerun, automatic retries, parameter sweep, GPU collection, or simulator/source modification. E2 stays at DRAM850 and changes only L1 miss queue 16 to 32. Its comparison reference is the already accepted r5 Vector at DRAM850/MissQ16, **not E1 at935**. These two one-factor points cannot identify the DRAM-frequency × queue-capacity interaction or predict their combined setting.

`/root/data/ep_memory_path_sensitivity_20261026_v1/tools/l1_plan.py` provides `build_config(destination)`. It verifies frozen hashes, preserves all bytes of the four historical env configs, then writes exactly one additional member `config-4.config`:

```
-gpgpu_cache:dl1 S:4:128:128,L:T:m:L:L,A:512:8,32:0,32
```

The line ends with one LF. Config order is 0,1,2,3,4. Existing members are never overwritten; destination must be absent or empty. The CLI only inspects sources and emits bounded JSON. The helper creates no cohort/spec/registration and launches no process. The main owner remains responsible for native qualification, scope binding, resource admission, execution, and scientific acceptance. Only tiny scripts/configs belong in this local preparation area; large input/result/archive assets default to genuine164.

## Field and production-gate evidence

PROVEN by read-only source review of Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`:

- `src/gpgpu-sim/gpu-cache.h:627–630`: sscanf binds the final groups `%u:%u,%u` to `m_miss_queue_size`, `m_result_fifo_entries`, `m_data_port_width`. Thus `16:0,32` → `32:0,32` changes queue capacity only. `A:512:8` MSHR settings, geometry, replacement/write/allocation policy, result FIFO and data width stay fixed.
- `gpu-cache.h:1852–1853`: legacy `miss_queue_full(num_miss)` compares queue size plus required entries against this capacity.
- `gpu-cache.cc:1782–1832`, `baseline_cache::send_read_request`: a lower-read requirement consults `lower_issue_slot`; on denial the cache records `MISS_QUEUE_FULL`, separately from MSHR entry/merge failures. Existing same-sector merge needing no lower read is distinct.
- `gpu-cache.cc:2193–2200`: the non-exact-L2 lazy-fetch write path also checks this queue; L1 write-through forwarding uses it. This is a shared read/write L1 forwarding queue test, not an L1 read-only-capacity claim.

No production source is changed or lazily fetched into protected trees. These citations were read through the GitHub connector at the exact commit.

## Baseline and same-unit metrics

Accepted Vector raw: `/root/data/ep_l2_main_vector_r5_20261023_v1/run/results/a6b61f77-2ff6-45ad-897c-df0812d01ae8/raw.log`, SHA256 `1f5519151cb381fbc370591d65e7ad78691435d5955ad99fea8dcdf7ffab0f6a`; frozen Core1093/main `e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33`.

Final `EPL2L1V1` at raw line29477 records accesses1,500,000, misses1,500,000, miss_queue_full1,240,787; line_alloc_fail/MSHR entry/merge/rw_pending are all0. The queue metric is retry events, not distinct requests or global stall cycles. Baseline q0 =1,240,787/1,500,000 =0.8271913333 retry events per accepted L1 access. Read retries1,228,130 and write retries12,657 are separate breakdowns, not additional events to add to the total.

Existing downstream evidence (26.50% channel-DRAM-cycle scheduler-full, 32.20% slice-L2-cycle input-full, DRAM byte-bandwidth utilization77.81%) makes queue buffering versus propagated service pressure an unresolved causal question. Full-window counters do not identify critical-path cycle contributions. Invalid `Bank_Level_Parallism_Col` is excluded.

## Proposed information-value gate, frozen before E1 observation

The 25% threshold below is an engineering selection rule for spending a single conditional run, not a statistical significance threshold or a physical phase boundary. No performance-sign or detach condition is used.

1. E1 must pass its exact identity/config/source/input, full instructions, commandlist, exit/drain, counters/closure, and scientific acceptance checks. If E1 is invalid or incomplete: do not start E2, do not retry E1 automatically, and preserve the failure.
2. Parse the **last application cumulative** L1 record from E1. Require accepted accesses=1,500,000 and a nonnegative integer MISS_QUEUE_FULL count. Missing/wrong-scope metrics mean HOLD with no start; do not manufacture values from other counters.
3. Let q1 = E1 MISS_QUEUE_FULL / E1 accepted L1 accesses. Recommend E2 only if q1/q0 ≥0.25, equivalently MISS_QUEUE_FULL ≥310,197 at the fixed access count. Otherwise skip E2 as low remaining L1-queue information value and preserve unused scope.
4. A worthwhile recommendation is not a launch. Main must still perform exact E2 native admission and resource checks under the one remaining conditional start. No auto-registration/start/retry is implemented in this helper.

E1 can improve cycles and still leave E2 informative: if residual queue retries remain above the gate, the independent question is whether increasing buffering at the original850 service point improves useful throughput or merely moves waiting into ICNT/L2/DRAM. If E1 does not improve cycles, E2 may still be informative under the same residual gate; this tests the queue-capacity hypothesis without selecting on a desired positive result. E1 positive/negative speedup, TagFAIL, and detach are deliberately absent from the decision inputs.

## E2 acceptance and interpretation

Compare E2 at850/MissQ32 to the old accepted850/MissQ16 reference, reporting cycles and full instruction/traffic/drain identities. Report L1 retry events per accepted access, useful request/response throughput, per-channel physical DRAM byte utilization, queue occupancies/full observations, and existing same-target-set joint Tag statistics. Keep denominators explicit: L1 retry events/access, channel-DRAM-cycle full rate, slice-L2-cycle full rate, and head-cycle Tag exposures are different units.

- Lower L1 retries with better cycles: supports buffering opportunity at the original service point; does not prove all saved cycles were L1 stalls.
- Lower L1 retries with flat/worse cycles and larger downstream queues: supports waiting migration or other limiting stages; retain as a valid negative result.
- Little retry/cycle change: weakens this specific16→32 buffering hypothesis; no further scan follows.
- New Tag pressure without cycle gain: pressure and performance opportunity remain separate claims.
- Zero TagFAIL/detach remains an acceptable outcome in every branch.

PROVEN: baseline queue retries and exact parser field. LIKELY: service backpressure contributes to those retries. UNKNOWN until an accepted E2: effect of16→32 on useful throughput, critical path, and target-set pressure. HYPOTHESIS: extra buffering may expose additional overlap, or simply redistribute waiting.

## Validation and boundaries

This turn reads frozen configs/source/raw and performs only bounded non-simulator CPU checks of helper syntax, byte-preserving config generation, final option precedence,850MHz retention, and decision boundaries using synthetic numeric inputs. Such checks are engineering validation, not application science or a result of E1/E2. No simulation, build, registration, epoch2-budget use, native-entry edit, registry edit, production-source edit, or protected-asset modification is part of this preparation. The main owner records any later actual run and authorization independently.
