# M4 integration authorization addendum

Status: **AUTHORIZED CONTRACT ADDENDUM**.

This addendum is the evidence-driven authorization layer for the previously
prepared M4 draft contracts:

- `M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
- `M4I_AB_INTEGRATION_AND_REPLAY.md`
- `M4C_LLM_BASELINE_CHARACTERIZATION.md`
- `M4B_SEGMENTATION_REPRODUCTION.md`

When this file is read through the explicit `M4_INTEGRATION_GOAL_START.md`
authorization, every `DRAFT ONLY / NOT YET AUTHORIZED` marker in those four
files is superseded. Their technical bodies are active except where this
addendum changes or tightens them.

The continuous target is:

```text
M4I A/B integration
 -> M4R formal replay compatibility
 -> M4C real-LLM baseline translation characterization
 -> M4B-P paper paging/sub-entry baseline
 -> M4B-S Weight Segmentation on real prefill/decode1
 -> M4B-CLOSEOUT
 -> STOP before M5 synthetic-KV pressure
```

Do not stop for ordinary successful transitions. Stop only at an explicit hard
STOP condition or the final M4B closeout boundary.

---

## 1. Accepted immutable source anchors

### Track A — VM baseline

Final accepted Core/GPGPU-Sim:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Repository/branch source:

`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Accepted M1-M3 Framework evidence source:

`47dde5767af8d30b892c7d63d932455644b7cf3a`

The Framework integration branch must start from the Track-A authorization
commit/descendant named by the startup instruction that contains this addendum
and the authorized start file. Later Track-A commits after `47dde576...` are
ChatGPT handoff/documentation only unless separately evidenced.

### Track B — accepted M4A merge preparation

Accepted Framework:

`e21ffebce280e6b932fb4556ef75c609ff54c326`

Repository/branch source:

`swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Accepted integration-manifest path:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/INTEGRATION_MANIFEST.md`

Git blob SHA of that manifest at the accepted B commit:

`291d749e7b96cc858f09335b052c6e37e5966b98`

Capture executable Framework:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Model/revision:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

The old Core `73774727e25fadf89df6f30ef5cf014091115db7` remains only a
frozen parser-compatibility evidence anchor. It must never become the integrated
VM Core.

---

## 2. Frozen formal archives

Prefill:

`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`

SHA256:

`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`

Decode1:

`/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`

SHA256:

`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`

No integration step may edit, repack, rename-in-place, or replace these accepted
archives.

---

## 3. Accepted semantic kernel classification

The old filename-only `0 NCCL` result is superseded and must never be reused for
semantic claims.

Formal prefill:

- total entries: 724
- `COMPUTE`: 692
- `NCCL_COLLECTIVE`: 32
- `MEMCPY`: 0
- `UNKNOWN_OTHER`: 0
- observed NCCL semantic families: 1

Formal decode1:

- total entries: 772
- `COMPUTE`: 740
- `NCCL_COLLECTIVE`: 32
- `MEMCPY`: 0
- `UNKNOWN_OTHER`: 0
- observed NCCL semantic families: 1

Observed NCCL family:

`_Z40ncclDevKernel_AllReduce_Sum_bf16_TREE_LLP11ncclDevCommmP8ncclWork`

Accepted derivative hashes:

| ROI | semantic full | compute-only | NCCL-only |
| --- | --- | --- | --- |
| prefill | `ee53ca249cd45e2fd4da6920db4038673636960d6f36f2f99789062412636908` | `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` | `9c899cd5312a8854e027db4c3415b934dfc0e9fd5e4a68c3d79a21055e978111` |
| decode1 | `9bb152d8475f7827e58071a7f765b2b00c5a2d08161a306f9031ff00a8f48701` | `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` | `c642daa4902c4d686e77934f2c9416a883ae170ccf5d18e67f86d6871ca84657` |

If external derivative files are absent at integration time, recreate them from
the immutable archives using the accepted B semantic classifier and require the
same hashes. Do not treat loss of a regenerable derivative as loss of the raw
formal capture.

### Trace-policy decision for M4R/M4C/M4B

Primary paper-facing one-partition policy:

`COMPUTE_ONLY_TP_PARTITION`

Required self-capture sensitivity/provenance policy:

`FULL_RANK0`

`NCCL_ONLY_DIAGNOSTIC` may be used for bounded diagnosis.

Reason: the paper specifies TP=4 and simulation of one partition but does not
publish how collective kernels were treated. Compute-only most directly models
the partition's compute stream, while the full rank-0 list preserves what was
actually captured. Neither is `PAPER_EXACT`.

If bounded M4R evidence shows NCCL materially changes translation behavior,
report both rather than silently selecting whichever better matches a paper
number.

---

## 4. Accepted full address-domain evidence

Track-B merge-prep fully decoded all 724 prefill and 772 decode1 traceg files,
with zero decoder invariant failures.

Prefill:

- lane references: 2,602,967,364
- requested bytes: 15,899,995,792
- max SimVA: `0x7fddf3808007`
- minimum required VA width: 47
- addresses `>=2^49`: 0
- addresses `>=2^56`: 0

Decode1:

- lane references: 815,478,621
- requested bytes: 4,771,296,188
- max SimVA: `0x7f81ecb88007`
- minimum required VA width: 47
- addresses `>=2^49`: 0
- addresses `>=2^56`: 0

Therefore **49-bit paper-facing VA mode is authorized** for these immutable
formal traces. No mask/truncation/canonicalization/relocation is needed or
allowed. Generic 56-bit mode remains a diagnostic/reference mode.

Accepted coverage artifact hashes:

- prefill final SHA256:
  `6fd209619fae6e348afd109933fe90cf9828d2e65d461b5dc50ccc90d6f4ab5a`
- prefill canonical SHA256:
  `6e5daf1e30d5555e9f76059b55a45f4d1f609af573082d7630621c280b6db81b`
- decode1 final SHA256:
  `dc56d89e0e3e6c1f1483fa560fdecf8d4183ac56c15b679911da094a2096c828`
- decode1 canonical SHA256:
  `60d213c6a057e7099dab0b17bb86faaa1b20519c892ec62f03e9e6e2d3e87858`

The VA-domain totals above do not depend on Weight/KV object classification.

---

## 5. Accepted object/page coverage — conditional integration recheck

Track B reported the following runtime-range matches:

| ROI/object | references | bytes | 64KB pages | 2MB pages |
| --- | ---: | ---: | ---: | ---: |
| prefill WEIGHT | 410,255,360 | 6,064,963,584 | 15,443 | 483 |
| prefill KV_CACHE | 54,935,552 | 158,466,048 | 64 | 3 |
| prefill UNKNOWN | 2,137,776,452 | 9,676,566,160 | 2,433 | 96 |
| decode1 WEIGHT | 63,799,296 | 1,012,989,952 | 15,443 | 483 |
| decode1 KV_CACHE | 26,136,448 | 195,661,824 | 82 | 4 |
| decode1 UNKNOWN | 725,542,877 | 3,562,644,412 | 119 | 19 |

Class-reference and class-byte sums conserve exactly in the accepted B report.
These labels remain `runtime-range matching`, not exact tensor-lifetime ground
truth.

### Mandatory M4I-RF0 range-index safety check

Independent review found one implementation risk in the accepted B coverage
utility: its helper merges WEIGHT ranges and KV ranges by class, while its
`RangeIndex` binary search assumes globally increasing start addresses. The
formal capture itself is unaffected, and the global VA-domain totals above are
unaffected, but Weight/KV/UNKNOWN attribution must be revalidated before it is
used for M4C or segment registration.

Before accepting object-specific coverage in the integration branch:

1. read the actual prefill/decode1 sidecars from the immutable archives;
2. construct the exact ROI-specific ranges used by B;
3. prove whether the B merged range list is globally monotonic by start;
4. add a directed test with KV below Weight and KV above Weight;
5. fix the integration copy of the analyzer so the final merged ranges are
   globally sorted by `(start,end,kind)` before building a binary-search index;
6. add an explicit assertion that `RangeIndex.starts` is monotonic;
7. strengthen resumable-partial identity for future scans so it binds not only
   the trace SHA, but also an analysis-contract identity covering at least the
   analyzer/schema version and ROI range-map/sidecar identity.

Decision:

- If the actual B merged lists were already globally monotonic, document that
  the old B object coverage is valid for these inputs, require the corrected
  range construction to produce the same ranges, and retain the frozen B object
  totals/hashes as accepted historical evidence. A full rescan is not required
  merely because the source utility is made safer.
- If either actual B merged list was non-monotonic, mark only the old
  **object-specific split** superseded, rerun full resumable object coverage for
  the affected ROI(s) with the corrected analyzer/contract identity, and bind
  new integration-local hashes before M4C. Do not recapture GPU traces.

Do not allow this check to rewrite the already proven 47-bit/global-address
facts unless a separate decoder inconsistency is discovered.

---

## 6. M4I address audit efficiency update

Because B already performed a complete active-lane decode with zero invariant
failures, M4I does not need to blindly rescan all 1,496 trace files just to
re-prove 49-bit eligibility.

M4I should:

- reverify the accepted archive and coverage hashes;
- run the M4I-RF0 range-index check above;
- validate representative decoded records against the integrated decoder;
- reuse the accepted full VA-domain result if all provenance/hashes match.

A full address rescan is required only if the accepted coverage artifact cannot
be reproduced/bound, decoder semantics change, or M4I-RF0 finds that corrected
object attribution requires it.

---

## 7. M4C concrete policy update

For paper-facing characterization runs on the formal traces:

- VA width = 49 bits;
- primary list = `COMPUTE_ONLY_TP_PARTITION`;
- `FULL_RANK0` = required bounded/full sensitivity according to M4R feasibility;
- no synthetic KV;
- object classes remain `WEIGHT`, `KV_CACHE`, `UNKNOWN`;
- object instrumentation must be behavior-neutral;
- replacement attribution must not affect victim selection/timing.

The generic 56-bit M3 LLM baseline remains useful as a control but is not the
paper-facing address-width setting once the 49-bit-safe evidence is admitted.

---

## 8. M4B paging/sub-entry policy remains authorized

Before implementation, P0 must still audit target paper/reference [4]/local
source for stronger sub-entry evidence.

If exact target/reference semantics remain unavailable, the already prepared
fallback is authorized:

`REFERENCE_APPROX_SUBENTRY_16`

for the 64KB paper baseline only, with the exact group/sub-entry semantics in
`M4B_SEGMENTATION_REPRODUCTION.md`.

Results using that fallback must be labeled:

`PAPER_PAGING_BASELINE_APPROX`

never `PAPER_EXACT`.

Do not tune sub-entry behavior to hit the paper's 95.9%/91.5% reference values.

---

## 9. M4B Segmentation policy remains authorized

Use the frozen formal contiguous Weight allocation/sidecar as the descriptor
source, never trace-pattern inference. The evaluated mechanism segments Weight
only.

The prepared parallel lookup model remains the default first reproduction:

- Segment and L1 launch together;
- default Segment service latency equals accepted L1 TLB service latency;
- Segment hit masks the conventional L1 result;
- Segment hit launches no L2-TLB lookup, MSHR, PWQ, walker, PWC, or PTE traffic;
- Segment hit fills neither L1 nor L2 TLB with the Weight translation;
- Segment miss reuses the already completed L1 result and never re-probes L1;
- non-Weight accesses remain on the selected paging baseline.

This timing is a project `MODELING_DECISION` implementing the paper's stated
parallelism without adding a serial penalty or an arbitrary faster Segment
advantage.

---

## 10. Required integration branches and final stop

Create fresh worktrees/branches; do not reuse either old A or B worktree.

Framework:

`hrl/vm-llm-m4b-v0`

Core:

`hrl/vm-llm-m4b-v0`

Core must branch exactly from:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Framework must branch from the exact Track-A authorization HEAD named in the
startup instruction.

Normal final stop:

`M4B-CLOSEOUT`

Do not start M5 synthetic-KV pressure, KV segmentation, page faults, migration,
UVM, MCM/chiplet behavior, multi-ASID study, or a new AI-aware mechanism in this
Goal.
