# W/V next architecture candidates

Status: **HYPOTHESIS / NOT_QUALIFIED engineering designs**, not patches, accepted policies or requests to start models. This task has zero additional application starts and performs no code edits. The priority is to finish attribution with the two already-authorized Stencil runs; a structure candidate should resolve a specific surviving question.

## Candidate 1: bounded optional-V retention informed by actual service

Evidence: accepted GEMM/FWT W-to-WV improves cycles about1.48%; historical Stencil has useful V service while Scan has low service per total counted retention area. That establishes a real benefit/cost tradeoff, not the effectiveness of C1 service-aware reclaim. A safe candidate could prefer reclaim of optional, unpinned, nonmandatory entries with no recorded service over equally eligible recently useful entries. Clean versus completed-dirty state may warrant separate treatment. Mandatory WB, active readers, generations, indexed ownership, pending responses and same-address ordering remain protected. Workload names and future knowledge cannot drive policy.

Cost to declare: at least a served bit or bounded timestamp/class, writes on actual service, candidate selection comparison/port/bank/color restrictions, finite scan/priority depth and any additional arbitration latency. Distinguish optional retention from WAD-mandatory WB staging. Replacing an existing finite eligible-entry choice can reuse hardware only with a concrete implementation argument; global zero-cycle associative search is not allowed. PPA and timing remain UNKNOWN.

Smallest engineering check: independent CPU fixture with unserved/served candidates, clean/completed-dirty, readers/pins/mandatory entries, same-color landing exhaustion, full directory, duplicate preview, response backpressure, generation and complete drain. The candidate must retain existing protected-state negative cases and terminate under continuous resource turnover. A trace that manually declares the future useful is an oracle and inadmissible as hardware performance.

Smallest later performance design, only after separate authority: one frozen new Core/ELF with policy OFF/ON in the same WV background, exact geometry/resources/ports/clock/input/certification; default OFF. Use an established positive input and a legitimate negative control selected before running, retain all outcomes. Same-newELF reference is required; no borrowing old Source78 cycles as that new-source reference. If new passive state is introduced, OFF/ON NI is mode-specific. Do not start until Stencil determines this is the remaining decision-changing policy question.

## Candidate 2: bounded directory negative-query filtering or query reuse

Evidence: accepted WV includes619,160 GEMM and150,462 FWT directory queries and equal one-cycle lookup-wait exposures; extra lookup cost is real. GEMM still benefits, so removing queries is not automatically the largest lever. An exact immutable per-head lookup token or finite conservative membership summary could reduce repeated/negative queries if the real production trace shows them. Repeated callbacks are not unique demand arrivals, and a negative-query denominator is currently not available in the accepted projection. **HYPOTHESIS:** some traffic could avoid directory work; **UNKNOWN:** actual incidence, additional avoided cycles or net benefit.

Cost to declare: summary lookup/update ports, bits, false-positive behavior, invalidation/version consistency, per-slice contention and pipeline timing. A filter must have no false negatives for a valid serviceable Victim entry; an exact cached head token must invalidate on directory mutation and owner/generation changes. Metadata lookup cannot become free merely by renaming it a precheck.

Smallest engineering check: insert/reclaim/promotion/WB completion races, repeated preview without mutation, head replacement, alias/generation mismatch, positive after prior negative, dirty-forward/readers, port arbitration and complete drain. Before a model proposal, use existing source/counters to identify whether a one-bit served/queried event distinction suffices. A new collector requires its own mode-specific CPU and application NI; S NI does not cover WV or F.

Smallest later performance design: same-newELF WV with filter/token OFF/ON and identical physical Payload/bank/query budget, declared extra latency, one qualified input known to have nontrivial negative-query demand. If that demand is not established, HOLD rather than running a broad matrix.

## Candidate 3: service arbitration between retained data and mandatory work

Evidence: W removes local copy/storage constraints in FWT yet lowerFIFO/MissQ pressure grows. WV reduces read demand and some W-only queue exposures; GEMM traffic shrinks strongly but application leverage remains small. **HYPOTHESIS:** a bounded priority rule could avoid delaying critical retained-read service or mandatory WB without increasing ports/queues. Full queues are not proof that an arbitration policy is the cause, and cumulative bank waits are not exclusive cycles.

Cost to declare: existing single-bank/port budget, finite request candidates, response capacity reservation, starvation age/fairness, WB progress credit and return-path arbitration. Extra queues, read ports or free metadata forwarding are separate architecture changes, not a software optimization. Keep no-readers/no-pins/ownership/sector restrictions and ordinary request fairness intact.

Smallest engineering check: adversarial retained-read/WB/fill mixtures, constant arrivals, per-bank color contention, response/ICNT backpressure, bounded mandatory progress, no double charge or resource leak, exact-once response and full drain. No speedup claim follows from fixture cycles.

Smallest later performance design: one same-newELF arbiter OFF/ON pair in exact WV or W background chosen by accepted pressure evidence; resource capacity/clock/service budgets equal. Main separately qualifies mode, source and NI and freezes the comparison. Do not enlarge MissQ/WAD/MSHR or change DRAM latency at the same time.

## Selection and measurement boundary

Prefer a single candidate only when an accepted result leaves its causal question unresolved. Current six endpoints do not support indiscriminate Payload expansion, more WAD/MSHR entries, a broad retention-length scan, ideal victim hits, free bank copies or a larger Tag-pressure sweep. FWT/GEMM establish a V-package effect but cannot separate clean/dirty service, fill avoidance, promotion, forwarding and lookup costs. Stencil conditional decisions determine whether retention/service is the strongest next mechanism lever. Scan remains separately authorized later if needed.

Minimum prospective passive counters, if essential: entries installed/reclaimed/terminal-censored by clean/completed-dirty kind; served-at-least-once bit at reclaim; service event count; first/last service interval; query population split by actual lookup outcome and request kind; capacity/port denial within the same eligible event population. Terminal live entries must be reported censored, not declared unserved-for-life. Reuse current event sites without extra probe/directory/bank operations, observer default OFF, bounded storage and per-mode NI. No new collector is implemented or required merely to finish this task.

Main must freeze exact spec, new Source5/ELF, input identity, mode eligibility, actual config echo, fair S/reference choice, resource costs, mode-specific NI and fresh scoped budget before any future application launch. Completed writes remain bounded by accepted no-forced-L2-flush semantics. Keep all positive/zero/negative outcomes, public evidence summaries and true164 recovery receipts. There is no claim of area reduction or physical timing closure.
