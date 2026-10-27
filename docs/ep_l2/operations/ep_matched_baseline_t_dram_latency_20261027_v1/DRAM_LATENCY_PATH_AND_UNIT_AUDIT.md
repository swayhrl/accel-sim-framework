# Latency path audit

Goal: EP_L2_MATCHED_BASELINE_T_AND_DRAM_LATENCY_CAUSAL_V1.
Scope: read-only exact Core c67b332db703f09571ba6628222c77d71440e141, tree2fdf60a69066a896e21d0ec1dd198977de058b75. Source root: /root/data/ep_tag_capacity_scaling_20261027_v1/core. No production source, old result, frozen tool, entry or scientific registry was modified.

## Decision

**PROVEN by source:** -dram_latency is an additive **cumulative GPU CORE-cycle counter** threshold on the real L2-to-MC fixed-delay queue, including the non-simple detailed-DRAM path. It is not a DRAM-clock-cycle parameter, a frequency, ROP delay, total memory-response latency, or DRAM chip CL/tRCD.

L0=100 and L1=200 therefore change this fixed-delay threshold only, by100 core-counter ticks. At unchanged1132MHz this nominal increment corresponds to88.339ns; actual eligibility is sampled only on850MHz DRAM events, with FIFO/scheduler/credit/backpressure effects. No end-to-end +100-cycle or speedup claim follows from that nominal increment.

**UNKNOWN until authorized production-linked CPU execution:** observed first-ready/MC-push off-by-one behavior and the complete response delta for this proposed fixture. Pure source/math checks below do not replace actual C++ execution.

## Exact accepted D identity

D cohort EP_TAGFLOW_VECTOR_D_S32_W8_T1_20261027_V1, UUID5e11a877-0219-4773-9ac3-f80166d1f20c.

- Spec SHA48d051b94b6dbea8cbf8ffb9026824db7d3a716c9e554594f67ea18ec7a4841d.
- Raw SHA7ec96ff09f13fd26469e508d1b357ecd1d696f5f693ddf254214008fdce64d5e,14191212bytes.
- Accepted point SHA6cc7f9dbac6f153e7d67b2eb9a8cd543931c79f447aebc65d68138936796baf8.
- Canonical source: Core c67; Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7; main ELF ad4421b441d1f8efef4c956381ede5e6fd7389147d26960931e202e0a38e4b07; static library74becb34ba74646e56109f181d4cbae61b2e94540171729754fa6b430f2547c9.
- Actual282 header: dram_latency100; simple_dram_model0; ROP160; clocks1132:1132:1132:850; FRFCFS1; scheduler128; DRAM return192; partition queues64:128:64:64; reserved WB credit1; separate write queue0.
- D geometry32setsx8ways,64subpartitions/32channels. Accepted cycles77237,56M instructions/15625CTAs/drain, actual production TagFAIL0 and detach0.

These are prior accepted D facts, not acceptance of a new condition.

## Source evidence table

Line references below are exact c67 source lines, relative to the source root.

| Subject | File/function/lines | Evidence and implication |
|---|---|---|
| Option registration | src/gpgpu-sim/gpu-sim.cc427-428, memory_config::reg_options | -dram_latency is OPT_UINT32 with default30. Help text alone does not specify its unit; use follows. |
| Distinct ROP option | gpu-sim.cc425-426; l2cache.cc2696 and1730-1740 | ROP has its own ready_cycle and precedes ICNT-to-L2 ingress. Its160 value must remain unchanged. |
| Real domain periods | gpu-sim.cc1277-1291, gpgpu_sim_config::init_clock_domains | Frequencies convert MHz to Hz; separate core/L2/DRAM periods. |
| Domain selection | gpu-sim.cc2100-2120, gpgpu_sim::next_clock_domain | Earliest physical clock event selects masks. Co-timed domains combine. |
| Core-counter increment | gpu-sim.cc2234-2267, gpgpu_sim::cycle | gpu_sim_cycle increments only under CORE, after DRAM and L2 work. ready_cycle compares this integer counter before the co-timed CORE increment. |
| Detailed dispatch active | gpu-sim.cc2178-2184 | DRAM mask invokes simple_dram_model_cycle only when simple=true; D simple0 invokes dram_cycle. |
| Early resource gates | l2cache.cc604-636, requires_dram_to_l2_return/can_issue_to_dram | Return-bearing packets require non-full destination DRAM-to-L2 queue and general credit. No-return L1/L2 writebacks may use reserved WB progress credit. |
| Detailed delay admission | l2cache.cc785-837, memory_partition_unit::dram_cycle | Round-robin subpartition search; can_issue and scheduler!full gates before lower pop. The admitted packet gets ready_cycle=current core-total+dram_latency, status DRAM_LATENCY_QUEUE, and a borrowed credit. At most one admission per channel/DRAM call. |
| Inclusive threshold/FIFO | l2cache.cc842-850 | Only queue.front is considered. Inclusive now>=ready plus scheduler!full causes pop and dram_t::push. A ready packet can wait longer; later entries cannot bypass a blocked head. |
| Service ordering | l2cache.cc778,829-849 | dram_t::cycle occurs before new ready packets are pushed. A packet pushed at this call cannot enter FRFCFS/bank service until a subsequent DRAM call. Latency0 could push in its admission call, but cannot receive same-call DRAM scheduling. |
| Delay storage | l2cache.h287-292 | std::list<dram_delay_t>, ready_cycle uint64. No independent configured delay-list capacity; outstanding credits and other resources bound admission. |
| General credits | l2cache.cc465-487,490-525 | Private1 per subpartition; shared=scheduler128+return192-(2-1)=319. With2subpartitions general outstanding ceiling321/channel; WB progress adds at most1 for eligible no-return traffic. This does not resize any queue. |
| Credit return and drain | l2cache.cc528-543,571-577,746-773,853-864 | Read credit returns only on transfer to destination DRAM-to-L2 queue; WB on actual set_done. busy includes latency queue and borrowed-credit ownership, so request absence from L2 queue alone is not terminal drain. |
| Scheduler gate | dram.cc164-178, dram_t::full | D shared FRFCFS scheduler pending count128 gates both initial delay admission and ready-to-MC transfer. This count excludes the fixed-delay list and other downstream states. |
| MC input | dram.cc251-273, dram_t::push | Sets MC_INTERFACE_QUEUE, pushes mrqq, increments n_req, runs normal memory-latency statistics. This is later than lower-pop acceptance. |
| Actual FRFCFS | dram_sched.cc207-254 | Next dram_cycle drains mrqq into scheduler, chooses a ready bank request and accounts its queue delay. |
| Actual column service | dram.cc559-636, issue_col_command | Requires active correct row, timing counters, turnaround constraints and non-full rwq; increments n_rd/n_rd_L2_A or n_wr/n_wr_WB per column burst. |
| DRAM timing domain | dram.cc535-552 | Timing counters decrement once per dram_t::cycle, hence DRAM events, unlike the core-counter fixed threshold. |
| DRAM completion | dram.cc294-317 | rwq drains only if internal returnq is not full. Completed returning reads enqueue there; no-return WB invokes set_done. Even no-return completion can be delayed by this shared rwq gate. |
| Return/backpressure | l2cache.cc750-773,1260-1299 | Destination full holds DRAM return head. L2 then accepts RO return or pays fill-bank service / waits for response queue. Returning to L2 is not final requester acceptance. |
| Upper response | l2cache.cc1225-1255; gpu-sim.cc2153-2169 | Descriptor stays live through actual response enqueue; ICNT buffer pressure may further delay consumption. |

Longer fixed delay may increase outstanding-credit residence, shift scheduler arrival order, and propagate through lower128, miss queue, banks, returns and frontend admission. These are causal possibilities, not additive wall-cycle components. No claim of a necessarily monotone application delta is made.

## Corrected counter interpretation for this Goal

**PROVEN:** prior accepted numeric values are unchanged; this audit corrects interpretation only.

- LIFE DRAM_ACCEPT is recorded at actual L2 lower queue pop: l2cache.cc1087-1093/1777-1780.
- LIFE DRAM_SERVICE is also recorded at that successful lower-pop acceptance, through l2_char_record_dram_success at1810-1822, called at820-823. It is **not** the column-command counter its old contract prose claimed.
- EPL2DRAMV1 successful_* values accumulate c7e_record_dram_success at399-409, called at822-823. The input boolean is requires_return, not is_write:604-607 classify all except L1/L2 writebacks as return-bearing. Thus successful_read_* means return-bearing admission payload, and successful_write_* means no-return WB admission payload. A generic ACK-bearing write can fall under the former label.
- EPL2DRAMV1 prints these payload bytes divided by sampled DRAM ticks*atom_size at896-915. Its name bandwidth_util does not make the numerator an actual bus-service counter.
- B0 scheduler_causal_block at1783-1800 means a lower-head attempt saw scheduler full while no return/credit blocker was observed. It does not count a ready-delay-list head blocked at842-850, and is not global stall cycles.
- C7E per-channel occupancy is sampled before m_dram->cycle at308-318/747; it does not expose fixed-delay-list occupancy or exact intratick high-water marks.

Consequently, frozen previous metrics f117's textual command-service label is not reused here. No frozen parser, raw data or source was rewritten to rename a counter.

## Actual command extraction from accepted D

True full-format counters: dram.cc699-711 prints per-channel n_rd,n_rd_L2_A,n_write,n_wr_bk,n_req,n_cmd. Full32-channel rows at the accepted final native clock77237 are complete. The extractor excludes abbreviated DRAM(id) rows, earlier cumulative snapshots, and uninitialized/garbage n_ref_event. It never sums repeated cumulative snapshots.

Actual D totals:

- Read column bursts, including alloc-read class:1,000,000.
- Write column bursts, including WB:470,316.
- Per-channel DRAM ticks57996; all-channel tick sum1,855,872.
- Burst bytes=BL2*busW16*chips1=32, from gpu-sim.h295-296 and actual options/full headers.
- Modeled read bus-burst bytes32,000,000; write bus-burst bytes15,050,112; total47,050,112.
- For this fully drained D, lower-pop payload totals happen to equal these service-byte totals. That empirical endpoint equality does not equate intermediate populations.
- n_req counts MC pushes, not column bursts. n_cmd counts all DRAM calls/ticks, including idle/NOP/row opportunities, not read+write commands.
- Optional gpgpu_n_dram_* helper scalars are not emitted in D; their cross-check is UNKNOWN. The complete split full32 rows provide the direct source counter evidence without them.

Pure module agent_b/dram_terminal_extract.py, SHA93d6140bc630f6e61f6e625b0613f926946bede4244102a9fca8640536d0617a.
API extract(raw,expected_final_cycle,effective_options); no writes/authority. Actual-D regression receipt DRAM_EXTRACTOR_ACCEPTED_D_REVIEW.json SHAe1fe9e9d9d75f92e88b9e5cd35d0ea797e62599aa39b83a5475d94bd79d35296.

## Executed versus pending

Executed only source reads, exact accepted-D raw/hash extraction, and tiny Python clock/queue/credit mathematics on CPU19/nice10/AS1GiB/wall60. Source/math receipt latency_source_math/7f43078f-28b9-4d42-bbc3-d4aa9eceb9dd/RESULT.json SHAd4d64bcd2779d26d2eb0130e8d23da5501ddc915255e9d9d12a69240bf71c27a. Initial optional-scalar extractor HOLD is preserved; it was a script assumption, not a model failure.

No simulator ELF, CPU C++ fixture, full application, native operation or GPU was executed by B. Production-linked CPU candidate and exact compile/run arguments are separate pending review. S/mode-aware observer closure is an independently reported C/main concern; this c67 latency-path audit does not waive it or claim a future source identity.
