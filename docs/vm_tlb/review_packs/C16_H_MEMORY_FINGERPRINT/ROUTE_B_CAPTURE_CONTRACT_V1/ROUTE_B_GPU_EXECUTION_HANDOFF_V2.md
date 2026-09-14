# Route B GPU execution handoff V2 — rental-GPU-first memory capture

STATUS=`AUTHORIZED_GPU_FIRST_PREP_AND_CAPTURE`

This V2 handoff supersedes only the execution policy in `ROUTE_B_GPU_EXECUTION_HANDOFF.md`.
The V1 evidence, limitations, schema, canary criteria, and provenance remain valid.

## 1. Why V2 exists

The existing formal Llama Route A trace is too narrow for memory/TLB/cache characterization:
it captures one selected static memory instruction per phase role. In Decode, the selected
SmallIndex instruction collapses to one observed VA per step. This is valid selected-PC
evidence, but it is not a phase working-set or memory-stream trace.

Route B therefore remains the correct next step: for selected exact representative kernels,
capture all and only direct `GLOBAL && has_mref=1` static instructions and all address-bearing
dynamic events. Route C is still required before claiming phase-wide representativeness.

The old V1 execution block was caused by the absence of an exact S0 phase-linked native census.
That is now an engineering gap rather than a fundamental blocker: Recovery-V3 has a working
campaign-scoped G1 parent-lease path on the rental RTX3090, and Qwen0 S3 has already produced a
real `.nsys-rep`, SQLite export, independent validation, and phase-linked catalog.

## 2. Cross-branch authority

Methodology/source branch:

- `hrl/vm-c16-h-memory-fingerprint-v0`
- minimum methodology checkpoint: `41875639c3638e4f4b8360e2542c09dfea14fa23`

Active GPU execution branch:

- `hrl/vm-c16-g-retry570-v0`
- minimum reviewed runtime checkpoint at handoff creation: `a4637744551d85339bb96ada396cd4fb0dac3cb0`

Do not checkout, merge, or reset the active G worktree to the H branch. Read H material with
`git fetch` + `git show origin/hrl/vm-c16-h-memory-fingerprint-v0:<path>`. The live G branch is
the execution authority and may advance beyond the minimum checkpoint.

Current G facts relevant to this handoff:

- Qwen0 S3 Prefill target V2 (`STG.E.128`, static index 4125) produced address-bearing R5 evidence
  and an independent repro under the frozen model/input/backend.
- Qwen0 S3 Decode V1 closed as `PREDICATED_OFF_TARGET`; that is a target result, not a tracer failure.
- Recovery-V3 campaign-scoped G1 has been restored and has produced a validated Qwen0 S3 census.
- Copyback is not a prerequisite for continuing GPU production when remote SHA/manifest closure is complete.

## 3. GPU-first policy

Rental-GPU time is the scarce resource. When any GPU-ready job exists, CPU-only work must not
leave the GPU idle for ordinary publication, copyback, local SHA, long documentation edits, or
nonessential audit work.

For every new GPU artifact:

1. close remote bytes/size/SHA256/manifest;
2. retain the remote source;
3. publish `COPYBACK_READY` or `REMOTE_SHA_CLOSED_COPYBACK_DEFERRED_GPU_PRIORITY`;
4. continue the next GPU-ready job;
5. Lane B may copy back later unless remote free space crosses the safety threshold.

Keep the existing hard per-window bounds: <=4 GiB raw and <=20 minutes. Partition rather than
silently widening a window.

## 4. Immediate Llama S0 unlock

Use the current Recovery-V3 campaign-scoped G1 machinery to regenerate an exact
`meta-llama/Llama-3.2-1B` S0/B1/T128/Decode4 native census on the RTX3090 under the frozen
revision/input/runtime identity. Do not write the historical ledger.

The S0 G1 deliverable must contain:

- real `.nsys-rep` with remote SHA;
- SQLite export with SHA;
- independent export validation;
- phase-linked kernel catalog with SHA;
- exact model/revision/input/scenario/runtime identity;
- parent lease and measurement-window closeout.

Only after this exact S0 census exists may formal Route B representative selection occur.
The old S1/S2 catalog remains methodology/reference only and is forbidden as S0 selection authority.

## 5. Route B V2 representative selection

V1 duration-mass selection remains a minimum guard, but memory characterization must not rely on
duration mass alone. Freeze selection before any new address outcome using the union of two
pre-outcome axes, independently per phase:

A. Duration axis:
- smallest deterministic exact-kernel prefix reaching >=70% native phase duration mass;
- preserve V1 tie-breaking and class-diversity rules.

B. Static memory-opportunity axis:
- after map-only discovery, compute a pre-outcome proxy per exact kernel:
  `launch_count * total_CTA_count * warps_per_CTA * static_GLOBAL_MREF_count`;
- rank by this proxy and include the smallest deterministic prefix reaching >=80% proxy mass;
- this proxy may use only census geometry/launch counts and static-map facts, never captured addresses,
  locality, cache/TLB outcomes, or mechanism performance.

Formal Route B selected set = union(A, B, class-diversity anchors actually observed in the exact census).
If the set becomes large, partition capture; do not silently drop kernels to meet a preferred count.
Publish the complete ranked census, both coverage cutoffs, and the frozen selected-function list before tracing.

## 6. Producer requirement — richer than current targeted-memory tool

The current retry570 targeted-memory tool is a single-static-index discriminator and is not a Route B producer.
Implement a new versioned NVBit 1.7.5 memory-event producer with all of these contracts:

- exact full-mangled function identity;
- exact code-object SHA and static-map SHA;
- sorted, SHA-bound static-index whitelist;
- whitelist rows must equal a declared subset of `GLOBAL && has_mref=1` rows;
- multi-MREF instructions must carry explicit MREF ordinal or fail closed;
- no LOCAL/SHARED/UNKNOWN row may enter a GPU-VA trace;
- append-only bounded output with overflow/drop counters and terminal record.

Every dynamic memory event must retain enough information for both fingerprint analysis and later
order-sensitive replay experiments:

- deployment/run/scenario/phase/decode-step;
- kernel launch id + exact function;
- CTA x/y/z, warp id;
- static index, instruction offset/PC, opcode, MREF ordinal;
- READ/WRITE/ATOMIC, width, memory space;
- active mask and predicate mask when available;
- active lane ids and per-lane GPU VAs;
- monotonic observed callback/event sequence (labelled `OBSERVED_CALLBACK_ORDER`, not hardware total order);
- terminal linkage.

Do not label this hardware timing order. It is sufficient for set/multiset/fingerprint analysis and may be used
for replay-sensitivity experiments only with that limitation stated.

## 7. Producer qualification before formal expansion

Qualification is mandatory but should be bounded and fast.

Q0 — CPU/parser fixture:
- synthetic records covering masks, predicate-off lanes, READ/WRITE/ATOMIC, widths, malformed space,
  multi-MREF rejection, output cap, overflow/drop terminal failure.

Q1 — tiny GPU memory fixture:
- deterministic cudaMalloc-backed GLOBAL load/store pattern;
- verify lane count, nonzero VA domain, access kind, width, masks, whitelist enforcement, terminal status.

Q2 — Llama bridge qualification:
- run the new producer with a one-index whitelist on an already-known exact Llama bridge function;
- compare structural counts/mask/width/opcode and line/bucket cardinalities against retained Route A facts;
- do not require cross-process absolute VA equality.

Only after Q0/Q1/Q2 PASS may the all-GLOBAL-MREF canary run.

## 8. Canary and formal Route B capture

For each selected exact kernel:

1. map-only discovery and semantic validation;
2. freeze all `GLOBAL && has_mref=1` indices;
3. estimate bytes/time before launch;
4. if needed, deterministically partition the sorted index list into disjoint contiguous groups;
5. run one bounded canary;
6. require identity, checksum, map, mask, lane, width, terminal, zero-drop, byte and time gates;
7. formal-capture all approved partitions.

A canary failure caused by volume may trigger deterministic pre-outcome partitioning. It may not trigger
address-result-driven target selection.

## 9. Route C coverage while the rental GPU is available

After a Llama S0 Route B producer/canary is qualified, and if rental GPU time remains, prefer collecting the
bounded Route C phase-wide reference now rather than postponing the GPU-dependent part.

Route C must keep independent <=4 GiB/<=20 min windows and may partition by predeclared launch/static groups.
Use it only to report structural coverage ratios (event count, requested-byte proxy, unique VA/line/page buckets).
Do not infer physical addresses, TLB misses, cache misses, or hardware global order from these traces.

## 10. Cross-model expansion during rental period

Once the producer is qualified, use otherwise-idle GPU windows to collect model-specific exploratory Route B data
for scenarios that already have lawful campaign-scoped G1 catalogs. Qwen0 S3 is the first candidate because its G1
catalog and address-bearing path are already validated. Qwen7/other models require their own lawful G1 first.

Do not reuse Llama static indices, kernel identities, maps, or target ranges across models/GPUs.
Do not promote exploratory cross-model captures to phase-representative claims until their own coverage validation exists.

## 11. 3090 vs future 4080

Treat RTX3090 and future RTX4080 as separate hardware identities. Re-run census/static-map/selection on 4080;
SASS, kernels, static indices, launch behavior, and VA streams may differ. Preserve the same high-level workload identity
for controlled cross-GPU comparison, but never reuse a 3090 static map or static-index whitelist on 4080.

## 12. Execution scheduling

While the Route B producer is being implemented/tested on CPU, keep the current G GPU queue running.
Do not wait for Route B code before consuming already-authorized G GPU work.

Recommended GPU work order:

1. consume current `hrl/vm-c16-g-retry570-v0` ready queue and complete already-qualified R5/R6 work;
2. run exact Llama S0 campaign G1 census to unlock Route B selection;
3. while CPU builds producer, continue lawful Qwen/Llama G1/R5/R6 rows;
4. as soon as Route B producer Q0/Q1/Q2 passes, run Llama Route B canary + formal partitions;
5. if time remains, run Llama Route C bounded reference and Qwen0 S3 exploratory Route B capture;
6. defer bulk copyback/publication until GPU queue is exhausted or remote-space safety requires it.

GPU idle >120 s with a GPU-ready job is a scheduling error unless blocked by a real measurement/process/identity/storage gate.

## 13. Required checkpoints

Commit+push compact evidence at these independent boundaries without waiting for the whole campaign:

- Llama S0 campaign G1 census complete;
- Route B V2 selected-function manifest frozen;
- producer Q0/Q1/Q2 qualification complete;
- first Route B canary result;
- each formal representative-kernel partition closeout;
- Route C reference closeout;
- each cross-model exploratory capture closeout.

Raw payloads remain outside Git.
