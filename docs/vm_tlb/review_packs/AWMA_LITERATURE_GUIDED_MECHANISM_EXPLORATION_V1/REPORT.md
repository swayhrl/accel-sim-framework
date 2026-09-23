# AWMA literature-guided mechanism exploration V1

Stage: `AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1`
Baseline comparator: `AWMA_RTX4080_SIM_BASELINE_V1` at framework authority
`8d1f14a32f5538660d74da86ccb03a2c504c5735`
Discovery targets: T0/T1/T2; these are not holdouts.

## Reading boundary

This is a bounded primary-source check, not a broad prior-art or novelty
review.

- [LATPC, MICRO 2025](https://yonsei.elsevierpure.com/en/publications/latpc-accelerating-gpu-address-translation-using-locality-aware-t/),
  DOI `10.1145/3725843.3756069`: the author-institution
  abstract was checked. It supports warp-instruction VPN regularity, TLB
  prefetching, MSHR compression and batched walks. The full method text was
  not available in this pass, so no implementation detail beyond the abstract
  is treated as verified and C1 is not a LATPC reproduction.
- [DEPOT](https://arxiv.org/html/2606.00486v1), arXiv
  `2606.00486v1`: Sections 4--7 of the original HTML were checked.
  The source specifies an 8192-bit, three-hash eviction-history Bloom filter,
  a pending set of at most 16 entries, a default 500K-cycle protection window,
  reset after 1024 history insertions, and invalid -> unprotected-LRU -> plain
  LRU fallback replacement. C2 deliberately adapts this method to the frozen
  AWMA platform rather than importing the paper's workload/platform results.
- [SnakeByte, HPCA 2023](https://pure.korea.ac.kr/en/publications/snakebyte-a-tlb-design-with-adaptive-and-recursive-page-merging-i/),
  DOI `10.1109/HPCA56546.2023.10071063`: the
  author-institution abstract was checked. Its recursive PTE merging depends on
  physical contiguity and a contiguity-aware allocator; it is context only.
- [*Towards Segmentation-Based Address Translation for LLM Inference*](https://pure.korea.ac.kr/en/publications/towards-segmentation-based-address-translation-for-llm-inference/),
  CAL 2026, DOI `10.1109/LCA.2026.3693796`: the author-institution abstract was
  checked. It explicitly assumes virtually and physically contiguous weights;
  it does not justify re-enabling dormant Segment F0 here.
- [cuPTW](https://maxkev1n.github.io/publications/sigmetrics-2026/)
  (SIGMETRICS/POMACS 2026): the author publication page was checked. It
  uses idle compute units, LDS caching and multi-lane page-walk execution. That
  controller/resource redesign is outside this low-cost pass.

No novelty claim follows from this list. A survivor requires a broader
closest-prior-art review.

## Candidate card C1: instruction-scoped same-page result sharing

Evidence label: `HYPOTHESIS` / `MODELING_DECISION`; LATPC-inspired AWMA
adaptation, not `PAPER_EXACT` and not a full-paper reproduction.

Source support: LATPC's checked abstract supports exploiting VPN regularity
within a warp instruction and coalescing translation work. It does not verify
this exact owner/member completion protocol.

Delta from frozen V1: resident coalesced accesses in one `accessq` are grouped
only when ASID, VPN, base-page size, mapping generation and access permission
class agree and neither access crosses a page. The front-most resident entry is
the owner and alone traverses the existing finite L1/L2/MSHR/PWQ/walker path.
Each member retains its UID and downstream data effect and derives only its
page offset from the owner's completed legal translation. Singleton entries
use frozen V1 unchanged.

Fixed first configuration, chosen before AI performance results:

- at most the resident warp instruction's bounded 32-entry accessq;
- no persistent result cache or future address information;
- existing translation lookup ports and queues for each owner;
- one member notification/application per instruction per cycle;
- existing `consume_ready` ownership is consumed only by the owner; no member
  creates or strands a controller READY entry;
- grouping is a bounded compare over resident accessq entries and overlaps the
  owner's lookup; no extra grouping pipeline cycle is modeled. This omitted
  explicit comparator-delay charge is a limitation, while delivery bandwidth
  is explicitly charged.

Expected mediators: nonzero shared deliveries, fewer physical lookup requests
and L1 probes at unchanged logical UID coverage, zero duplicate application,
and complete lookup/controller drain. Negative controls are singleton,
different-page, different-ASID, permission-mismatch, generation-mismatch and
cross-page cases.

Novelty status: unknown. Same-VPN MSHR merging already exists in the baseline;
C1 tests hit/READY service sharing that the accepted source audit did not find.

## Candidate card C2: bounded eviction-history refill protection

Evidence label: `PAPER_SPEC` for the DEPOT method above;
`DOCUMENTED_APPROX` / `MODELING_DECISION` for the AWMA adaptation.

Delta from frozen V1: only the shared standard L2 TLB gains eviction-history
metadata and protection-aware victim selection. L1/L2 capacity, associativity,
ports and lookup latency remain frozen. On an L2 miss with a history-filter
hit, one exact key enters a 16-slot pending set; its eventual refill is
protected for 500K cycles. Invalid ways win, then unprotected LRU, then plain
LRU when all ways are protected. A full pending set drops protection metadata,
never demand work.

Fixed first configuration, chosen before AI performance results:

- 8192-bit Bloom filter with three fixed hashes;
- reset before the insertion following each block of 1024 insertions;
- 16 exact pending keys with duplicate merge;
- 500K-cycle window, 20-bit start time plus one valid bit per 768 L2 entries;
- all protection-valid bits clear at each 20-bit timer epoch transition,
  avoiding stale wraparound at the cost of shortening a window that crosses
  the boundary;
- invalidation/flush clears candidate history, pending and protection state;
- ordinary LRU fallback guarantees progress under all-protected pressure.

Declared storage is 25,419 bits (3,177.375 bytes): 8,192 Bloom bits,
`768 * 21 = 16,128` per-entry timer/valid bits, 1,088 bits for 16 pending keys
(32-bit ASID + 33-bit VPN + 2-bit page-size class + valid), and an 11-bit
insertion counter. Hash/replacement logic and observational counters are not
included in that storage sum.

Expected mediators: history hits, protected refills/hits, protected-victim
skips, fallback activity, and L2 miss/walk changes. A low-eviction workload is
a valid inactive negative control. This implementation does not claim DEPOT's
published speedups or exact SM86/4KB/1024-entry environment.

Novelty status: none claimed; this is a direct literature-inspired adaptation.

## Pre-screen correctness

The candidate unit test covers same/different key, ASID, permission,
generation, page boundary, OFF LRU behavior, history detection, protected
refill/hit, protected-victim skipping, all-protected fallback, pending-state
drain and timer wrap reset. Existing timing, pending-retry and runtime
validation tests pass with mechanism OFF and with C2 selected.

The first integrated A1 smoke passed, but the initial AI C1 points exposed a
coverage-sensitive liveness defect: an accessq head cohort member could launch
its own normal lookup while waiting for the owner, then receive the owner's
shared result and strand that independent READY entry. The pre-fix T0/T2 runs
ended with 24,216/132,531 READY entries and are retained as
`PRE_FIX_INVALID_READY_LEAK`, never as performance evidence.

The repair makes a cohort head wait for the owner/member path and therefore
prevents that second lookup. The repaired A1 10/80 smoke completed for OFF, C1,
C2 and the service-control ablation with full unique-UID coverage, zero
untranslated/unobserved, zero duplicate applications and empty
lookup/MSHR/PWQ/walker/candidate state. Repaired C1 delivered 39,936 members
and changed A1 cycles from 875,138 to 863,057. A1 is a cheap opportunity
control, not AI evidence and not a tuning input.

## Initial discovery results

Every admitted AI point preserves instructions/CTA identity, full logical UID
coverage, zero untranslated/unobserved, zero duplicate application and terminal
controller/candidate drain.

| Target | OFF cycles | C1 cycles | C1 cycle change | C1 shared deliveries | C2 cycles | Finding |
|---|---:|---:|---:|---:|---:|---|
| T0 | 527,896 | 487,624 | -7.6288% | 2,722,464 | 527,896 | C1 promising; C2 inactive |
| T1 | 665,802 | 653,485 | -1.8499% | 6,629,952 | 665,802 | C1 small positive; C2 inactive |
| T2 | 93,079 | 94,034 | +1.0260% | 132,544 | 93,079 | C1 regression; C2 inactive |

C1 reduces physical L1 probes from 3,101,682 to 369,387 on T0, from
7,169,938 to 531,081 on T1, and from 412,391 to 279,190 on T2. Walk starts are
unchanged at 256/493/134 respectively. Thus the initial response is associated
with suppression of redundant hit/lookup service, not fewer page walks. T2 is
an important counterexample: service traffic falls but one-member-per-cycle
delivery overhead outweighs it.

C2 records zero L2 evictions, history insertions, history hits and protected
refills on all three AI targets, so it is `INACTIVE_ON_THIS_SCREEN`, not a
failed implementation. Its direct eviction-positive test remains PASS.

## Cost and limitations

- C1 adds no modeled persistent cache/CAM capacity and reuses the bounded
  accessq and its existing applied/result fields. It requires a bounded
  within-instruction equality network, owner selection and a result-delivery
  mux. Comparator delay is overlapped with owner lookup rather than charged as
  a new pipeline stage; only one member delivery per cycle is allowed. This is
  an optimistic timing limitation that independent hardware work must cost.
- C1 preserves one logical UID and one downstream access/side effect per
  member, but it is not LATPC MSHR compression, prefetching or batched PTW.
- C2's declared 25,419 bits exclude hash/replacement combinational logic and
  statistics. The simulator uses convenient host containers; the declared
  hardware representation, not host allocation size, is the modeled cost.
- C2's zero opportunity on these targets prevents any AI performance claim;
  the directed eviction-positive test establishes implementation activation,
  not workload usefulness.
- T0/T1/T2 all come from the same accepted Qwen2.5-0.5B campaign. They expose
  operator diversity but not model-family generality, and none is a holdout.
- The frozen `BASE_CONCURRENCY_MODEL_RESIDUAL` and model-relative 10/80 latency
  interpretation remain unchanged. No platform parameter was tuned.

## Follow-on discrimination and validation plan

Because C1 is promising on T0, one matched T0 0/80 diagnostic and one T0
`service_control` ablation are added. The ablation retains cohort detection and
owner-first scheduling but makes members pay their own normal translation
service; it distinguishes service suppression from grouping/reordering alone.

The matched 0/80 result is 496,170 cycles OFF versus 489,880 for C1, a 1.2677%
cycle reduction. At 10/80, the reduction is 40,272 cycles; at 0/80 it is only
6,290 cycles, so removing modeled L1 lookup latency removes 84.38% of the
absolute saved cycles. Walk starts remain 256 in every T0 arm.

The service-control ablation is correct and quiescent but takes 957,758 cycles,
an 81.4293% increase over OFF. It has zero shared deliveries and restores
3,091,446 L1 probes versus 369,387 for C1 (OFF: 3,101,682), while retaining the
same 256 walks. This separates the useful intervention from owner-first
grouping: eliminating redundant lookup service is necessary for the observed
T0 benefit, while grouping without result sharing is strongly harmful.

The bounded conclusion is therefore: C1 is promising on T0, modestly positive
on T1 and regresses T2; C2 is inactive on this screen. This is not broad LLM
benefit, novelty, or a paper conclusion.

The next discriminating experiment after review should freeze the current C1
source and compare one-versus-two finite member-delivery slots on T0 and T2,
with the added mux/port cost declared. That directly tests whether T2's
regression is notification serialization while retaining identical physical
lookup suppression; it is not started automatically here.

T0/T1/T2 and A1 are discovery data, not holdouts. No admissible independent
model-family trace is currently frozen: the available Qwen3/DeepSeek assets
lack an accepted historical runtime/input binding. Independent confirmation
should therefore freeze the mechanism first, then use the first future
SM89-compatible trace with (1) a different model family or invocation,
(2) immutable model/input/trace hashes, (3) no use in this exploration or prior
parameter choice, and (4) the same OFF/candidate state-generation sequence.
No capture or model download is started by this Goal.
