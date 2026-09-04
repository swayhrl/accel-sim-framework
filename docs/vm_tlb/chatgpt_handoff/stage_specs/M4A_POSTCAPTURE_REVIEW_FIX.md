# M4A post-capture review fix

## Status

**AUTHORIZED NOW.** The expensive GPU data-acquisition Goal has completed and both formal archives have already been copied to the main development server with matching remote/local SHA256 values. This stage is a **main-server closeout repair/audit only**. No further GPU capture is authorized or required.

Accepted data-acquisition anchors reported at entry:

- Framework final Goal lineage: `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`, with final evidence/report descendant `df825709ca1f195fa490f3d806d970591949bb12`;
- formal prefill archive: `/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`;
- formal prefill SHA256: `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`;
- formal decode1 archive: `/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`;
- formal decode1 SHA256: `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`.

The purpose is to independently audit the copied artifacts, repair stale review-pack files, tighten scientific/provenance statements, and produce a clean handoff for M4B/M5. This stage must not modify Core M1-M3 semantics, recapture data, implement Segmentation, or inject synthetic KV.

## Why this review fix is required

Independent ChatGPT review of `df825709...` found that the underlying capture evidence is largely convincing, but several review-pack files are stale and still describe the historical blocked Goal state. In particular, at review time:

- `SOURCE_ANCHORS.md` still referenced blocked G0 source anchors;
- `HOST_ENVIRONMENT.md` still described a blocked G0 with 982 GiB free;
- `GOAL_GATE_RESULTS.md` still showed G4 RUNNING and G5-G8 NOT_STARTED;
- `RAW_LOG_INDEX.tsv` still marked formal prefill/decode1 as `NOT_CREATED`;
- `FORMAL_DECODE1.md` is too terse compared with `FORMAL_PREFILL.md`;
- `OPEN_ISSUES.md` correctly flags address coverage and NCCL policy, but the zero-NCCL classification needs a precise offline audit rather than an assumption.

These are documentation/evidence-quality issues, not reasons to recapture the already checksum-verified formal bundles.

## RF0 — Independent archive re-verification

On the MAIN development server, independently verify both formal archives before editing documentation:

1. exact file exists;
2. SHA256 matches the frozen values above;
3. zstd/tar archive listing succeeds;
4. internal `SHA256SUMS` verification succeeds;
5. expected run directory exists in each archive;
6. expected sidecar, workload manifest, raw/full kernels list, classifier output, trace files, logs, and provenance/checksum files exist.

Record commands/results. Do not trust the existing Markdown summary as a substitute.

If either archive fails integrity, STOP as `POSTCAPTURE_REVIEW_BLOCKED`.

## RF1 — Repair review-pack consistency

Update `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/` so every file reflects the completed Goal.

At minimum repair/enrich:

- `SOURCE_ANCHORS.md`;
- `HOST_ENVIRONMENT.md`;
- `GOAL_GATE_RESULTS.md`;
- `FORMAL_PREFILL.md` if needed;
- `FORMAL_DECODE1.md`;
- `COPYBACK_CHECKSUMS.md` if needed;
- `RAW_LOG_INDEX.tsv`;
- `VALIDATION_SUMMARY.md`;
- `OPEN_ISSUES.md`;
- `STORAGE_CAPACITY_MODEL.md` if audit changes any numbers.

Required source-anchor distinction:

- capture-source SHA(s) used for the successful formal runs;
- subsequent documentation-only evidence closeout SHA(s);
- parser Core SHA;
- local model snapshot/revision identity.

Do not imply that `df825709...` was necessarily the executable capture source if it is a later documentation-only descendant.

`GOAL_GATE_RESULTS.md` must show G0-G8 final statuses consistent with `GOAL_PROGRESS.md`.

`RAW_LOG_INDEX.tsv` must identify the formal prefill/decode1 copied artifacts/log roots rather than historical `NOT_CREATED` entries.

## RF2 — Formal decode1 evidence parity

Expand `FORMAL_DECODE1.md` to the same evidence level as `FORMAL_PREFILL.md`.

Include, from actual archive contents/logs:

- exact run ID;
- frozen model/revision/TP/B8/S64/G3/BF16/rank0-only contract;
- ROI boundary statement;
- raw trace count and size;
- traceg count and size;
- kernelslist SHA256;
- classifier counts;
- Weight/KV sidecar summary;
- absence of `SYNTHETIC_KV`;
- archive path/SHA256/integrity result;
- parser-smoke result and its scope;
- any timing data actually recorded.

Do not invent missing timing/peak-disk data.

## RF3 — NCCL presence/classification audit

The formal manifests currently report:

- prefill: 724 COMPUTE, 0 NCCL, 0 MEMCPY, 0 UNKNOWN;
- decode1: 772 COMPUTE, 0 NCCL, 0 MEMCPY, 0 UNKNOWN.

Because real TP=4/NCCL execution was used and rank-selective NVBit materially slowed rank0 enough to require a longer distributed timeout, determine offline what the zero-NCCL trace classification actually means.

Using the copied archives only:

1. inspect the raw/full `kernelslist.g` names for both ROIs;
2. search case-insensitively for likely collective/kernel tokens (`nccl`, `allreduce`, `all_gather`, `allgather`, `reduce_scatter`, `reducescatter`, `broadcast`, `collective`, `send`, `recv`), while avoiding false positives;
3. report representative first/middle/last kernel names and unique-name counts;
4. inspect the tracer/classifier behavior sufficiently to distinguish:
   - no NCCL kernels captured by the tracer path;
   - NCCL kernels captured under names missed by classifier rules;
   - collectives occurring outside the profiler ROI;
   - another evidenced explanation.

Do not change the raw trace. Do not make a permanent paper-exact keep/drop decision.

If the exact reason remains unproven, state it as `UNKNOWN` and preserve the observation that real TP/NCCL runtime was used but formal raw lists contained no classifier-recognized NCCL entries.

## RF4 — Address/object coverage feasibility audit

Current sidecars provide one rank0 contiguous Weight range and 128 real KV events, but the review pack says trace-address coverage is unavailable.

Without modifying capture data, determine whether the copied `traceg`/raw trace format contains enough memory-address information to perform an **offline streaming coverage analysis** against the sidecar ranges.

At minimum answer:

- can memory references be extracted from the copied traces without simulator semantic changes?;
- can Weight-range hit count/bytes and KV-range hit count/bytes be computed?;
- can UNKNOWN/unclassified accesses be measured?;
- can this be done per ROI and optionally per kernel?

If practical within this stage, implement a read-only analyzer under an appropriate project utility/test path and run it on both formal bundles. If the full scan is expensive, a streaming implementation is preferred; do not load all trace data into memory.

Any analyzer result must clearly distinguish transaction/instruction/reference counts and bytes. Do not infer tensor identity from patterns outside the sidecar ranges.

If a full coverage scan is not practical now, record a precise next-stage implementation plan and keep coverage `UNKNOWN`.

This item is important for M4B/M5 because later Segmentation/AI-TLB analysis must know whether trace addresses actually align with the recorded Weight/KV object ranges.

## RF5 — Parser compatibility strengthening

Current formal evidence only proves bounded startup/binding on ordinary compute kernels. Preserve that limitation.

Using the copied data and frozen parser Core `73774727e25fadf89df6f30ef5cf014091115db7`, perform a broader but bounded offline compatibility audit without changing Core semantics.

Preferred evidence:

- enumerate unique kernel names / representative kernel positions;
- parse/start a representative sample spanning early/middle/late kernels and distinct kernel names for both prefill and decode1;
- record any unsupported opcode/format failure;
- do not claim full performance simulation.

If a cheap parser-only/header validation can cover all trace files, use it. Otherwise use a documented representative sample. Do not spend days simulating every kernel.

## RF6 — Storage-capacity model audit

Recheck `STORAGE_CAPACITY_MODEL.md` against actual copied archives and any retained logs.

Current reported observations are:

- local model snapshot: 2.48 GB;
- CUDA 12.6 toolkit: 7.46 GB;
- venv: 5.31 GB;
- NVBit tree: 10.6 MB;
- formal prefill raw: 3.365 GB;
- formal prefill traceg: 161 MB;
- formal prefill archive: 3.527 GB;
- formal decode1 raw: 738 MB;
- formal decode1 traceg: 37 MB;
- formal decode1 archive: 774 MB;
- free disk: 978 GiB before prefill, 970 GiB before decode1, 968 GiB after decode1;
- true peak temporary footprint: UNKNOWN because it was not sampled.

Do not fabricate a peak. Compute and document:

- observed persistent baseline footprint;
- observed per-ROI final/raw/postprocessed/archive footprint;
- lower bound on required capacity from observed data;
- why temporary peak cannot be known exactly;
- minimum/recommended/conservative future disk recommendations with explicit safety rationale;
- which remote files may be deleted after verified copy-back.

Retain or adjust `100 GiB minimum / 250 GiB recommended / 500 GiB conservative` only if the evidence supports those labels. Make clear these recommendations apply to this Llama-3.2-1B Route-E workload, not automatically to 8B/GLM/DeepSeek.

## RF7 — Closeout and release recommendation

Update `docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md` and `GOAL_PROGRESS.md` only as needed for final consistency.

Create a short release section stating whether the rented GPU instance is safe to power off/release.

`SAFE_TO_POWER_OFF` requires:

- both main-server formal archives independently reverified;
- all required non-regenerable evidence is inside the copied archives or otherwise persisted on the main server;
- Git evidence/review pack is pushed;
- no additional GPU-side validation is required for this review fix.

Final status exactly one:

- `POSTCAPTURE_REVIEW_PASS_SAFE_TO_POWER_OFF`
- `POSTCAPTURE_REVIEW_BLOCKED`

After explicit-path commit/push, STOP. Do not start M4B/M5/Segmentation/synthetic KV.
