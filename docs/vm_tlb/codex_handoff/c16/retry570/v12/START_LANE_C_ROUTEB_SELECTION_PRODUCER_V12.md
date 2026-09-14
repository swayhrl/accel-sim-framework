# START — Lane C Route-B selection and producer V12

Use Goal mode.

This is a CPU/code lane. Do not run model workloads, nsys, NVBit, NCU, or any scientific GPU job.

Read:

```bash
git fetch origin hrl/vm-c16-g-retry570-v0 \
  hrl/vm-c16-g-retry570-chatgpt-handoff-v12 \
  hrl/vm-c16-h-memory-fingerprint-v0

git show origin/hrl/vm-c16-g-retry570-chatgpt-handoff-v12:docs/vm_tlb/codex_handoff/c16/retry570/v12/C16_GPU_FIRST_MULTI_WINDOW_HANDOFF_V12.md

git show origin/hrl/vm-c16-h-memory-fingerprint-v0:docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/ROUTE_B_GPU_EXECUTION_HANDOFF_V2.md
```

Create/use a separate worktree and development branch from the latest `hrl/vm-c16-g-retry570-v0`, e.g.:

`hrl/vm-c16-g-routeb-producer-v0`

Never modify Lane A's active worktree.

## Goal 1 — produce GPU map requests immediately

Use the exact Llama S0 campaign G1 catalog already published on active G.

Do the minimum CPU analysis required to create a first frozen `ROUTE_B_MAP_REQUESTS` batch as quickly as possible.

For Prefill and Decode independently:

1. group rows by exact full function identity + grid/block + shape/dtype evidence available in the catalog;
2. compute launch count and native duration mass;
3. rank deterministically by descending phase duration mass, ties by full function identity then geometry;
4. choose the minimum duration-prefix reaching >=70% of phase duration, or at least three distinct eligible classes when available;
5. include any actually observed semantic-class anchors required by the H V2 methodology;
6. do **not** use any NVBit address/locality outcome.

Output and commit/push a compact request file containing only exact map requests needed to calculate the memory-opportunity proxy. Each request must include:

```text
request_id
phase
exact full function
known mangled name if authoritative, else MAP_DISCOVERY_REQUIRED
grid/block
launch_count
phase_duration_ns
phase_duration_fraction
selection_reason
source_catalog_sha
```

Checkpoint immediately after this batch. Report the commit to Lane A so GPU map-only work can start. Do not wait for the producer implementation.

## Goal 2 — consume map summaries and freeze final selection

As Lane A returns map summaries, compute for each candidate:

`memory_proxy = launch_count * CTA_count * warps_per_CTA * static_GLOBAL_MREF_count`

For each phase choose the minimum deterministic prefix covering >=80% proxy mass. Final selection is:

`duration-prefix U memory-proxy-prefix U observed-semantic-class-anchors`

Freeze a final selected-kernel manifest before any Route-B address canary. It must include complete ranking tables, cutoffs, coverage fractions, exact function identity, geometry, map SHA, static GLOBAL+MREF list/hash, and forbidden outcome-based selection rules.

If a mapped candidate is absent or not exact-identity-resolved, fail that candidate closed and continue with other deterministic candidates; do not substitute by short kernel name.

## Goal 3 — implement Route-B producer

Extend the exact-function targeted infrastructure into a versioned append-only multi-static-index producer.

Requirements:

- exact full-mangled function gate;
- actual code-object SHA verified against path;
- static-map SHA verified;
- sorted static-index whitelist + whitelist SHA;
- emit only predeclared `GLOBAL && has_mref=1` rows;
- explicit MREF ordinal; reject unsupported multi-MREF ambiguity rather than silently using operand 0;
- per-event run/scenario/phase/decode-step, launch id, CTA xyz, warp id, static index, instruction PC/offset, opcode, access kind, width, active mask, predicate mask when reliable, active-lane IDs, per-lane observed GPU VA, observed callback sequence, terminal linkage;
- sequence is named `OBSERVED_CALLBACK_ORDER` and is not hardware-global time;
- drop and overflow counters;
- formal admission requires drop=0, overflow=0, terminal COMPLETE;
- bounded host output cap;
- no raw payload in Git.

Do not weaken the existing single-target diagnostic semantics.

## Goal 4 — Q0 CPU qualification

Build parser/unit fixtures for at least:

- READ/WRITE/ATOMIC;
- width;
- active mask and lane count;
- predicate semantics;
- multi-MREF rejection/handling;
- invalid memory space rejection;
- whitelist SHA mismatch;
- map/code-object mismatch;
- overflow/drop;
- missing terminal;
- deterministic partition union/no-overlap.

Q0 must pass before requesting GPU Q1.

## Handoff to Lane A

After Q0 PASS, push the development branch and report:

```text
ROUTEB_DEV_COMMIT=
ROUTEB_MAP_REQUEST_COMMIT=
ROUTEB_SELECTION_MANIFEST_COMMIT=
PRODUCER_SOURCE=
PRODUCER_Q0=PASS|FAIL
FOCUSED_TESTS=
GPU_Q1_READY=YES|NO
```

Lane A decides when to integrate between measurement windows.

## Do not block on

- copyback;
- publication prose;
- long markdown cleanup;
- unrelated asset work.

Ordinary implementation bugs should be solved in this Goal without asking the user unless there is a real external blocker.