# CODEX Goal — Lane E / 174-new
## AWMA R101R3 bounded service → producer-backed handoff screen V1

Date: 2026-09-29

This is one continuous, solve-and-continue Goal for **Lane E = 174-new**.
Do not rename Lane E/F/G. Do not start work on Lane F or Lane G.

## 0. Scientific purpose

Accepted authority already establishes:

- Lane E execution authority:
  `97d5be184b7f7f35c06d3ee111a8c5ba6efad896`
  (`R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`).
- B0 measured ROI = 2,985,319 cycles.
- O2 measured ROI = 1,130,670 cycles.
- O2 reduction = 62.1256555832%.
- O2 is a post-translation / pre-L1 one-cycle **unbounded service oracle**, not hardware.
- Lane F / 109 authority:
  `0210143098cbf3993b4f1a38a39852aaaf006183`;
  S128 Native remains MIXED and is not a causal decomposition of L512 O2.

This Goal asks only:

1. how much O2 headroom survives when normal L1 + interconnect are retained and service is bounded by the existing L2-subpartition hit path; then,
2. only if that survives, how much survives when service requires data to have been supplied by real producer stores into a finite 4 MiB handoff buffer.

This is a screening/diagnostic architecture round. It does **not** claim novelty.

Use arm names below to avoid confusion with Lane F:

- `S1_PARTITION_HIT_SERVICE`
- `H1_PRODUCER_BACKED_HANDOFF_4M`

## 1. Exact starting authority

Repository:
`swayhrl/accel-sim-framework`

Create an execution branch/worktree from exact parent:

`97d5be184b7f7f35c06d3ee111a8c5ba6efad896`

Do not merge experimental branches.

Must read before changes:

- `docs/vm_tlb/review_packs/AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/FINAL_DECISION.md`
- `.../O2_DESIGN_AND_SCOPE.md`
- `.../O2_CONTEXT2_RESULTS.tsv`
- `.../ROI_COMPARISON.tsv`
- `.../CONTEXT2_KERNELS.tsv`
- `.../CONTEXT2_RUNTIME_SIDECAR.tsv`
- `.../O2_CORE.patch`
- `.../RUN_RECEIPTS.json`
- `docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/FINAL_DECISION.md`
- accepted platform authority `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`.

Large traces/raw remain on node164 and are read directly through the existing mount.
**Do not stage/copy large trace payloads onto 174 local disk.**

## 2. Hard inherited constraints

- All new simulator functionality is opt-in and default OFF.
- Functional switches and diagnostic-only telemetry switches remain separate.
- OFF must reproduce the accepted comparator; do not alter baseline defaults.
- Normal VM translation remains enabled.
- Preserve original SimVA/SimPA/data mapping.
- Preserve original global instructions, coalescing, dependencies, CTA/kernel order and compute.
- Preserve LDGSTS pending/DEPBAR semantics, LDG scoreboard semantics, store ACK accounting and normal response arbitration.
- No future-trace knowledge.
- No free data appearing in H1.
- No kernel fusion/reordering, no NS-step/coefficient/tile-map change.
- No cache-capacity/latency/queue parameter sweep.
- No FULL5 unless explicitly permitted by the survivor rule below.
- No new Native/NCU/NVBit capture.
- No 109 GPU work.
- No scratchpad/DSMEM/cluster mechanism in this Goal.
- No automatic baseline promotion and no novelty claim.

Engineering problems that do not change scientific identity/semantics/claim boundary: solve and continue.
P2/P3/P4 missing wrappers/index/tmp are deterministically reconstructed under existing V5 policy; do not convert them into a scientific STOP.
STOP only for unrecoverable scientific payload/identity loss, required semantic change, or an unavoidable claim-boundary change.

## 3. Stage A — existing-evidence decomposition, NO simulator rerun

Before implementing S1, consume accepted O2/B0 raw/source and publish a compact evidence table.

At minimum extract, **without new simulation**:

### A1. Existing queue depth
From accepted O2 raw/log/source, recover and report:

- `awma_r101r2_service_max_scheduled_depth`
- `awma_r101r2_service_max_ready_depth`

If the counters were emitted in raw but omitted from final TSV, parse them.
Do not rerun O2 for this.

### A2. Per-kernel boundary
For measured kernel 4/5/6 (XXT / BA / BMM-add), recover any existing exact end-cycle/cumulative counter boundaries available in accepted raw.
If accepted raw does not expose an exact field, mark it **NOT AVAILABLE FROM ACCEPTED RAW** rather than inferring a fake number.

### A3. Region × opcode composition
Using immutable accepted traces + runtime sidecar, offline classify measured-ROI qualified accesses by:

- kernel 4/5/6,
- region A/B/X0/X1 + generation,
- LDG,
- LDGSTS,
- WRITE,
- transaction count,
- request bytes / active bytes when available.

Do not change trace bytes and do not use simulator future knowledge.

### A4. Producer/consumer availability ledger
Offline derive a bounded ledger for each 128-B line/sector in A/B/X:

- which real producer store first supplies it in the six-member CONTEXT2,
- which later consumer reads can legally use that produced generation,
- whether the relevant producer occurs inside context or measured ROI,
- region death/generation boundary.

This is a **data-availability ledger**, not a global-cache chronology/MRC.
Do not claim actual cache residency from it.

Publish Stage-A tables before interpreting S1/H1.

## 4. S1 — finite partition-side service screen

### 4.1 Question

O2 bypasses normal L1/L2/interconnect service before L1.
S1 asks:

> if a legal transient request still experiences normal L1 behavior and normal interconnect delivery, but data is guaranteed available at its L2 subpartition and is served at the normal modeled L2-hit service cost/bandwidth, is measured-ROI cycle response still material?

S1 is still an oracle for **data availability**, but not for unlimited pre-L1 service.

### 4.2 Required placement

Source-audit the accepted memory path first.

Qualified traffic must:

1. complete normal VM translation;
2. undergo normal L1 behavior;
3. traverse the normal request interconnect;
4. arrive at the normal L2-subpartition ingress / scheduler;
5. only then use S1.

A request satisfied by L1 must never reach S1.

### 4.3 Required resource semantics

Prefer implementing S1 as a special **always-hit transient class inside the existing L2-subpartition hit path**, not as a separate unbounded side queue:

- use the existing L2 request/ingress queueing;
- use the existing modeled L2 hit latency/pipeline;
- use existing response/writeback arbitration;
- use existing return interconnect bandwidth;
- no extra response port;
- no unbounded request or ready queue;
- do not update/allocate ordinary L2 data/tag residency merely because S1 oracle-data exists;
- nonqualified traffic follows baseline L2/DRAM unchanged.

If the current source cannot express this literally, implement the closest bounded equivalent whose queue depth, service rate and latency are taken from the **accepted existing L2 hit path**, not invented/tuned constants. Document the exact source/config anchors. Do not choose values by performance outcome.

S1 can reuse the accepted A/B/X region/generation qualification.
Atomic/unsupported/partial/multi-region/stale accesses fail closed to the normal hierarchy.

### 4.4 Activation protocol

For the L2 S1 screen:

- kernels 1-3: S1 service **disabled**; exact B0 context behavior required;
- kernels 4-6: S1 enabled.

Thus B0/O2/S1 share the matched context boundary.

### 4.5 L1 directed qualification

Before CONTEXT2, prove at minimum:

- default OFF and explicit-none equivalence;
- qualified read;
- qualified LDGSTS read;
- qualified write/store ACK;
- L1-hit request cannot be double-served by S1;
- nontransient normal path;
- atomic/unsupported/partial/multi-region/stale fail-closed;
- finite normal L2 hit-path latency/service behavior;
- no added return port/bandwidth;
- duplicate completion = 0;
- outstanding = 0 at drain;
- translation coverage and existing VM/controller gates remain closed.

Use small directed/T2-derived inputs only.
Do not run a parameter sweep.

### 4.6 B0 reuse rule

The accepted B0_CONTEXT2 and O2 results may be reused only if the new S1-capable binary in OFF mode passes exact accepted OFF-equivalence on the inherited directed/integrated signatures and source/config/input identities are unchanged.

Do **not** rerun long B0 merely for bookkeeping.
If OFF-equivalence reveals an engineering bug, fix it and repeat the small qualification.
If exact OFF semantics cannot be restored without changing baseline behavior, STOP.

## 5. L2 screen #1 — S1 CONTEXT2

Run exactly one S1 CONTEXT2 point after L1 qualification.

Primary metric:

`ROI = end(kernel6) - end(kernel3)`

Compare with accepted:

- B0 = 2,985,319 cycles;
- O2 = 1,130,670 cycles.

Report S1:

- ROI cycles;
- improvement vs B0;
- full CONTEXT2 cycles;
- per-kernel available boundaries;
- L1/L2/DRAM activity;
- S1 qualified/served/fallback counts;
- queue/service occupancy or backpressure counters from the existing bounded path;
- LDG / LDGSTS / WRITE split;
- all correctness/drain gates.

### S1 gate

`S1 improvement >= 5%` → S1 survives; proceed to H1.

`S1 improvement < 5%` → STOP H1 long simulation.
Interpret only:

> the large pre-L1 O2 headroom does not survive this bounded partition-side placement strongly enough in the accepted CONTEXT2 screen.

Do not expand to latency/queue scans and do not move S1 closer to SM inside this Goal.

If S1 fails, publish Stage A + S1 result and close.

## 6. H1 — producer-backed 4 MiB handoff buffer
### Only execute this section if S1 survives

H1 asks whether S1's surviving service opportunity can be supplied by **real producer stores**, with finite storage, without removing the original global store path.

### 6.1 Storage organization

Fixed single configuration. No capacity sweep.

Logical total data capacity target:

`4 MiB`

Rules:

- 128-B lines;
- distribute physically across the same L2 subpartitions using the accepted address→subpartition mapping;
- use the accepted L2's set-index/replacement style where practical;
- choose an exactly representable total capacity **<= 4 MiB** if exact geometry requires rounding; never round upward;
- document exact total/per-subpartition bytes, sets, ways and line count.

This is a separate handoff data array; it does not enlarge ordinary L2 capacity.

Each entry must include enough identity to avoid stale service:

- physical line tag / accepted translated identity appropriate to the subpartition;
- region id;
- generation;
- 4 × 32-B sector-valid mask at minimum;
- valid/replacement state.

If implementation uses finer byte-valid information, report it; do not silently assume a partially produced 128-B line is fully valid.

### 6.2 Producer fill semantics

A qualified producer WRITE continues through the **normal baseline memory hierarchy exactly as before**.
H1 never suppresses the backing global store in this Goal.

In parallel, H1 may capture a copy at the partition-side handoff structure:

- only from a real qualified producer store;
- only sectors actually written become valid;
- finite fill port/rate;
- no backpressure to the baseline store merely to make H1 look better;
- if H1 fill resources are busy/full, drop/evict the handoff copy and count it;
- no infinite victim buffer;
- no free spill path.

An unsupported/atomic/ambiguous write intersecting a resident H1 line must fail closed so stale handoff data can never be served.

### 6.3 Consumer hit semantics

A qualified consumer READ can hit H1 only when:

- exact line identity matches;
- region/generation is current/live;
- all requested sectors are valid;
- request arrived at the same partition-side point used by S1.

H1 hit uses the **same bounded service/response path as S1**.

Otherwise the request falls back to the normal L2/DRAM path.

No cross-subpartition lookup/broadcast.

### 6.4 Lifetime

Reuse the accepted PRE/POST region/generation authority.

- stale generation entries never hit;
- POST-dead entries may be lazily invalidated/first victims;
- no future last-read knowledge;
- no prediction is required.

### 6.5 CONTEXT2 warm-up protocol

CONTEXT2 begins after normalization, so H1 must not fabricate an initial X copy.

For kernels 1-3:

- normal B0 memory service remains authoritative;
- H1 may **capture real producer stores only** to build handoff state;
- H1 read service is disabled;
- capture is nonblocking and finite; unavailable fill opportunities are dropped/counted;
- normal B0 cycles/instructions/CTA/L1/L2/DRAM context signature must remain exact.

This allows context BMM to provide the real next-X generation for measured ROI without artificial preload.

For kernels 4-6:

- producer capture remains active;
- H1 consumer service is enabled.

If capture-only context cannot be made timing-neutral without a new behavioral assumption, do not silently relax the matched-context contract: STOP for scientific review.

### 6.6 H1 L1 directed tests

Before long run, prove:

- empty buffer miss/fallback;
- exact producer store → later legal consumer hit;
- partial sector fill cannot satisfy wider read;
- generation mismatch miss;
- death invalidation/lazy-dead behavior;
- capacity/conflict eviction;
- fill-port busy/drop behavior;
- no baseline store suppression;
- LDG and LDGSTS hit completion path;
- store ACK unchanged;
- unsupported/atomic intersect invalidation/fail-closed;
- no duplicate completion;
- drain quiescence;
- exact context capture-only timing neutrality on a small integrated test.

## 7. L2 screen #2 — H1 CONTEXT2

Only after S1 >=5% and H1 L1 qualification.

Run exactly one H1 CONTEXT2 point.

Primary ROI is again:

`end(kernel6) - end(kernel3)`

Report at least:

- ROI cycles and improvement vs accepted B0;
- full CONTEXT2 cycles;
- exact context-match receipt;
- H1 exact capacity/geometry/metadata upper bound;
- producer fill attempts / admitted fills / fill drops / evictions;
- consumer reads / hits / misses / normal fallbacks;
- A/B/X × kernel × LDG/LDGSTS split;
- sector-valid misses;
- generation/death misses;
- max occupancy;
- bounded service/backpressure counters;
- ordinary L1/L2/DRAM counters;
- correctness/drain gates.

### H1 gate

`H1 improvement >= 5%`:
- freeze exact H1 configuration/source/binary;
- mark it as an **L3 promotion candidate only**;
- do not tune capacity;
- proceed to Section 8.

`H1 improvement < 5%`:
- do not try 8/16/32 MiB;
- diagnose using the frozen counters:

  - low hit / high capacity or conflict loss → finite data availability insufficient at 4 MiB under this organization;
  - high hit but low cycle response → service is hidden or another residual dominates;
  - high fill loss → finite capture bandwidth is the binding cost.

Publish and STOP. Do not invent a second H1 variant inside this Goal.

## 8. L3 rule — only for an H1 survivor

If and only if H1 >=5%, do **not** immediately run a broad matrix.

First freeze H1 and perform one source/contract review for:

1. a capacity-matched control that adds comparable storage without producer-consumer handoff semantics; and
2. FULL5 activation semantics (including normalization, all five NS iterations, generations and drain).

Then:

- if a clean capacity-matched control can be defined without changing the scientific contract, run:
  - H1 FULL5,
  - one capacity-matched FULL5 control,
  using existing accepted FULL5 trace only;
- no new 109 capture;
- no capacity/latency sweep;
- no holdout/new model in this Goal.

If defining the matched control requires a new architectural assumption or changes the claim, STOP after freezing H1 and request review rather than improvising.

The L3 result remains model-relative simulator evidence, not RTX4080 hardware speedup.

## 9. Interpretation table to use

Final report must explicitly distinguish:

### S1 <5%
O2 depended materially on its more optimistic pre-L1/unbounded placement; partition-side bounded-hit service does not retain material response in this scope.

### S1 >=5%, H1 <5% because hit/availability is poor
A partition-side service opportunity exists, but this 4 MiB real-producer handoff cannot expose enough data under the frozen organization.
Do not conclude all producer-consumer handoff is impossible.

### S1 >=5%, H1 hit high but H1 <5%
Data handoff works structurally, but its latency is largely hidden / another residual dominates.
Do not increase capacity.

### H1 >=5%
Finite resources + real producer-derived availability + normal fallback retain material response.
This justifies L3 and a later closest-work/novelty review; it does not itself establish novelty.

Never subtract O2/S1/H1 percentages and call the difference "L1 cost", "ICNT cost", or "cache time".

## 10. Execution efficiency

Before long runs, check CPU/RAM/I/O/node164 health.

S1 and H1 long CONTEXT2 runs are scientifically gated:
H1 long run must not start unless S1 passes.

However, while a frozen S1 long run is executing, CPU-only report preparation and H1 source reading/direct-test planning may proceed if they cannot mutate S1's running binary/config/output.

Each run gets independent output/config/log/tmp/receipt paths.
Immutable trace inputs may be read-shared.

Do not high-frequency poll long simulator jobs.

## 11. Deliverables

Create a compact review pack, suggested root:

`docs/vm_tlb/review_packs/AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1/`

At minimum:

- `README.md`
- `STAGE_A_EXISTING_EVIDENCE.tsv`
- `REGION_OPCODE_COMPOSITION.tsv`
- `PRODUCER_CONSUMER_AVAILABILITY.tsv`
- `S1_DESIGN_AND_COST.md`
- `S1_DIRECTED_TESTS.tsv`
- `S1_CONTEXT2_RESULTS.tsv` if executed
- `H1_DESIGN_AND_COST.md` if S1 survives
- `H1_DIRECTED_TESTS.tsv` if S1 survives
- `H1_CONTEXT2_RESULTS.tsv` if executed
- `L3_RESULTS.tsv` only if legitimately promoted/executed
- `FINAL_DECISION.md`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- `CHANGED_FILES.md`
- `SHA256SUMS`

Large raw stays on node164; review pack contains hashes/indexes/receipts, not copied traces.

## 12. Closure

At completion:

- commit exact source/tools/review pack;
- push exact commit;
- use bounded transport fallback (HTTPS → HTTP/1.1 → GitHub SSH → gh/API) if needed;
- fetch-back / remote SHA+tree verify;
- preserve accepted scientific raw;
- clean worktree;
- report final commit and STOP.

Do not auto-merge into accepted baseline.
Do not start Lane F/G work.
Do not start another mechanism after a negative result.
