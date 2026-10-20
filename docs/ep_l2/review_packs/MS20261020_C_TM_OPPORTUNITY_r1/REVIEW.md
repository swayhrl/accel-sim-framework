# C T/M opportunity analysis, bounded first revision

The strongest current candidate is **Conv for M**, not yet for T. Existing main61 **S** has genuine line-MSHR refusals, but no observed all-pending Tag-set refusal. FWT is a particularly useful **zero-RO T/M negative control**, even though it has ordinary memory/writeback pressure. These choices use source, input proofs and non-F structural observations only. No F performance or F counter file was read, no application was started, and no production RO semantics changed.

## Exact source and evidence boundary

Current A2 formal producer is Core `d010911e3174a3764791183cd108fe4664ba8731`, runtime Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`, main SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`. This supersedes Core27/main773 as current producer identity. Existing Core27 audit/failure evidence is still historical evidence under its own identity. Read-only fetch of the current Core branch verifies d010911e. RO transactions/runtime/store-port and l2cache.cc are byte-identical to Core27; no transfer of unrun fixture qualification is implied.

OBSERVATIONS.json contains exact paths, hashes and source identities for every consumed file/object. The analysis reuses D's complete-epoch oracle metadata and E's existing artifact reviews, historical B0-Legacy CSV, and only completed main61 Conv S E010. It does not open any original trace body, SQLite database, new capture, F terminal/log/counter file, or ongoing application log. Registry access is identity/status routing only; paired performance endpoints are not used. Historical B0 is Core ece1a3a/Framework f08d2ce at its original geometry, not new C16/D512 evidence.

Input-model-only labels describe the evidence consumed by C here; they neither grant nor revoke E's later source-specific profile acceptance. In particular, historical oracle-review runtime_qualification=false must not override the newer main61 producer acceptance record retained in the same snapshot. No existing E qualification or result state is changed by this analysis.

The final bounded analysis used one CPU, a256MiB address-space cap, and read13,724,108 file bytes plus373,693 source-object bytes in0.269s. Current process VmHWM was50,286,592B. Two preceding tiny metadata passes and their outputs are retained: one exposed inherited ru_maxrss accounting, the next wrote valid data but exited1 on a stale print-field name. The print was repaired and the final pass exited0. Total file reads across all three were41,172,324B; no trace scan/build/native test occurred. Raw ru_maxrss is retained separately and is not misreported as parser-phase memory. Do not repeat completed analysis merely while waiting for dependencies.

## Actual current Conv S pressure

E010 COMPLETE_VALID uses the exact current source/main61 with T=M=V=W off and the ordinary finite16-slot WB background. The profile/config/trace identity is in OBSERVATIONS.json. Its full S raw log hash was verified. Repeated cumulative dumps are deduplicated by keeping the last application record for each of64 slices; summing all three dump occurrences would be wrong.

| Observation | Value | Interpretation |
| --- | ---: | --- |
| Line-MSHR peak in a slice | 128 | Reaches the real128 line-record capacity |
| LINE_MSHR_FULL distinct requests | 1,824 | At least this many S frontend heads encountered the guard |
| LINE_MSHR_FULL request-wait sum / refusal observations | 40,088 /40,088 | Across slices and requests; max302 per request, not40,088 saved global cycles |
| Pending Tag peak in a slice | 128 | Material pending ownership, not automatically a full set |
| Simultaneously reserved Tags in one set, maximum | 7 | Real same-set pending concurrency, below16 ways; not proof of >16 eligible RO misses |
| TAG_SET_PENDING observations | 0 | No directly observed T pressure in this S run; earlier guards can hide downstream checks |
| Shared descriptor peak / full refusal observations | 425 /0 | D512 is not shown full here; old D256 pressure must not be transferred |
| WB_DATA_SPACE requests / wait sum | 33,572 /848,913 | Strong W-space context to cross-check with B |
| COPY_PIPELINE requests / wait sum | 546,865 /546,865 | Paid finite-copy context; S reports546,865 logical copy reads and writes each |
| SAME_ADDRESS_WB requests / wait sum | 925 /638,854 | Potential V relevance; operation kind and post-eviction read overlap still unknown |
| DATA_SERVICE requests / wait sum | 394,444 /433,239 | Bank/service competition can remain after tracking relief |

Observer durations/reasons overlap. They are neither an exclusive stall decomposition nor fractions of application execution time. Zero visible Tag/descriptor refusals does not prove those resources were always free behind an earlier guard. Same-set reserved counts include native non-RO owners; they are not an eligible-RO concurrency histogram. E010's configured RO admission, detach and line-avoidance counts are zero because both switches are off, not because the opportunity was measured absent. RO-on actual application counters and final critical benefit remain UNKNOWN in this first revision: no F metrics were consulted to select or promote candidates.

This narrows the initial generic hypothesis: neither the historical B0 table nor this current S run supports claiming a known Conv Tag-set-full bottleneck. Current S supplies the positive M-pressure evidence that the older table lacked.

## Candidate profiles for D and B

RO percentages below are **read lane reference fractions in the whole-epoch offline model**, not L2 requests, unique line fractions, cache misses, native admission or detach probabilities. Conv's original certificate is unchanged. All other model artifacts retain their exact input hashes and E artifact-review status; no new C runtime qualification is granted. Unknown/held input is never labeled RO usable.

| Workload | Model RO lines / RO read-lane fraction | Historical B0 line-MSHR max / one-set reserved max | First-version role and risk |
| --- | --- | --- | --- |
| convolutionSeparable | 294,912 /49.895% | 126 /7 | Primary M-opportunity candidate: **current S** reaches128 and refuses1,824 requests. Broad RO model subset plus W/copy/same-address-WB pressure. T pressure and certified-read intersection with those waits unresolved. |
| vectorAdd_4M | 250,000 /100% | 92 /3 | Broad-coverage contrast, not a proven T/M bottleneck. Old descriptor-full2,176,663 is D256 context and is not avoided by M. Streaming/coalescing may create siblings that protect Tags; runtime parent mix unknown. |
| cfd_097k | 51,612 /36.532% | 68 /4 | Secondary certified-subset contrast with weaker old tracking pressure. No old Tag/line-full refusal. Eligibility must remain exact-input native-qualified; no positive T claim. |
| dwt2d | 24,576 /13.437% | 59 /4 | W-dominant cross-mechanism contrast: old WAD-full74,044 and scheduler281,249, but no old Tag/line/descriptor-full events. Small RO/read intersection and epoch structure may limit T/M. |
| sad | 396 /2.295% | 7 /1 | Nonzero-coverage **low-pressure negative control**. Old line/Tag/descriptor-full observations all0. Preserve all older withdrawn sad scientific claims; this is only the exact listed input's model/structural evidence. |
| FWT_7_21 | 0 /0% | 102 /5 | Primary **zero-eligibility T/M negative control** under the unchanged whole epoch. All131,072 globally read lines also have same-line stores;41,943,040 read-lane references excluded. Can retain W/memory pressure without an RO mechanism target. No per-kernel proof substitution. |
| SGEMM medium | UNKNOWN /UNKNOWN | 22 /3 | D has a complete syntax/non-atomic input candidate, E registration pending and no independent RO certificate. Conditional low-pressure contrast only; not an RO-use candidate or automatic replacement. |
| btree | Historical model3 lines; **not usable** | 69 /5 | Native nonzero-mask input scope HOLD overrides old model coverage. Host updates between kernels remain part of proof obligations. No qualification revival. |
| Scan, SpMV | UNKNOWN; **not usable** | Old structural data retained | D found concrete input syntax/mask failures. Scan's old Tag/descriptor pressure is not a reason to promote an invalid input; no repair/recapture here. |

Historical B0 line-MSHR-full observations are0 for all seven original workloads in this projected table. For example, Conv old descriptor-full3,373,327, WAD-full8,266 and scheduler2,510,412 are historical structural context, not evidence that M fixes descriptor capacity or that current D512 is full. The historical same-set column is the maximum over kernel/slice records, not a time fraction or an ordered miss trace.

The immediate handoff is **Conv(primary M+W/V intersection hypothesis), FWT(zero-RO negative), SAD(low-pressure nonzero-coverage negative)**. VectorAdd tests coverage-versus-pressure; DWT separates W pressure from T/M opportunity. No additional full run or change to D's roster/budget is requested by this handoff.

## reuse_seen: why a large RO subset can still have little T opportunity

**Source fact:** successful admission resets reuse_seen=false; successful merge sets it true after D512 reservation. The test is independent of original_mf. Sector children of a128B parent have separate UIDs/descriptors; child0 admits and a later sibling merging while that transaction is live sets the same sticky bit as another parent's repeat. The bit is not cleared by a partial fill or waiter retirement. Only a later successful admission resets the inactive slot's entry.

Both can_detach and detach require T, attached, !reuse_seen and some required sector not ready. Relief is attempted on requested-set reservation failure and scans Tag indices for an eligible owner. Thus even an eligible certified request is not itself a detach event. For a128B parent whose four children arrive before completion, siblings alone can keep the Tag attached until transaction retirement; they can suppress T without suppressing M. This is a real conservative source restriction, not a measured sibling frequency for these applications. A32B singleton can detach before any merge if actual same-set pressure requests relief. A later repeated read can then create duplicate lower work when M removes the conventional line index; that traffic/landing cost must be reported.

**Unresolved application question:** existing offline lane-address summaries do not identify actual L2 mem_fetch parent UIDs, interconnect arrival order, L1 filtering, or live outstanding ownership. A warp memory instruction with many lanes is not proof of one128B L2 parent, and static address/set concentration is not proof of simultaneous pending misses. The first revision therefore does not invent a sibling percentage, an exact number of missed detach opportunities, or new same-set congestion from SM trace order.

M bypasses a conventional **line record per admitted transaction**, not one D512 descriptor per child/merged request. Existing normal_line_allocations / avoided_line_allocations count admission events; accepts/merges/requesters and lower packets have different denominators. After detachment M=0 can rediscover the old transaction through the native line index; M=1 cannot use that index and may pay for a separate same-line landing. Do not infer combined T+M benefit by adding independent counter totals.

## Required evidence ladder and A2/E2 requests

| Stage | Required identity/observation | This revision |
| --- | --- | --- |
| Whole-epoch offline RO subset | Full command/body/proof hashes, read/write/atomic/alias/host exclusions, legal native input | Existing exact model subsets; btree/Scan/SpMV held, SGEMM unknown |
| Eligible L2 access | Actual global demand read after native coalescing/L1/partitioning, covered line, open exact epoch | Workload event intersection UNKNOWN |
| Actual RO admission | accepted_ro, transaction admits and merges, shared D512/capacity and TVD-before-RO routing | S switches off; RO-on workload counts not consumed |
| Successful T detach | stats.detached, actual Tag generation/landing handshake and pending obligation | Workload counts UNKNOWN; R35 remains FAIL |
| M avoidance | avoided_line_allocations versus normal allocations, with line-record peak and rejection | S positive line-full evidence; RO-on avoidance UNKNOWN |
| Critical waiting / final benefit | Exact-profile actual wait/overlap, residual bank/WB/return costs, independent same-source qualification | Current S waits known; joint certified intersection and causal benefit UNKNOWN |

A2/E2 should first reuse already available legitimate **non-F or predeclared mechanism diagnostic** exports where present. If a new observer/test is necessary, review before implementation/run: observation-only counts of sibling-parent merges versus independent-request reuse, protected pending owners encountered at a real detach-relief attempt, successful detach, and exact certified-read/line-full/set-full overlap. No guard exemption, reuse_seen clear, additional address CAM, earlier completion, input rewrite or kernel-only certificate is authorized. Existing success/avoidance/duplicate-sector/lower-concurrency counters should be reused; do not add redundant simulated state.

Future profile comparisons remain E2-owned at the original fixed W/V background and T/M cells, with exact source/config/binary/trace/oracle identity and remaining cumulative40 budget. This revision does not launch, reserve or require those comparisons. Final application-cycle attribution cannot be recovered from sums of wait counters alone. Any necessary source/fixture adaptation is A2-owned; exact new native-input qualification is E2-owned.

**B cross-check:** the current S Conv W-space/copy/same-address-WB evidence and historical DWT WAD/dirty context give concrete intersection candidates. Ask B to intersect its actual post-eviction read / retained WB / directory/paid-slot evidence with the same input IDs and time/request scope. A same-address WB wait may be a writer and is not automatically a V-readable reuse; dirty residency alone does not establish a victim hit. No new B workload-profile acknowledgement is assumed. Preserve B's actual guard counterexample and its source-specific repair history.

## Preserved boundaries

R35 original failed source/input/logs stay frozen. C's original combined fixture and replacement split128/joint32 controls retain their actual unrun status; no source equivalence is relabeled as native PASS. Original Conv certificate/generator, complete-epoch host-update exclusions, empty-certified-range native fallback and every earlier withdrawal remain intact. Current production source is not modified, no binary rebuilt, no trace recaptured or input rewritten, no E registry/budget edited, no new Goal or waiter created. D receives the candidate profiles and limitations; A2/E2 receive only clearly identified unresolved measurement/qualification requests.
