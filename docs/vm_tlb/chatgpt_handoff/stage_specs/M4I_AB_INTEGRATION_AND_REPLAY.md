# M4I / M4R — A/B integration and formal LLM replay contract

Status: **FUTURE CONTRACT / DRAFT ONLY — NOT YET AUTHORIZED**.

Parent contract:

`M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`

This stage starts only after ChatGPT has accepted Track B's
`M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION` and issued an explicit authorized
start handoff with all `<B_...>` placeholders resolved.

---

## I0 — admission and clean branch creation

### Required immutable inputs

Track-A Core:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Track-A Framework integration start:

`<A_INTEGRATION_HANDOFF_SHA>`

Track-B accepted merge-prep Framework:

`<B_ACCEPTED_FRAMEWORK_SHA>`

Track-B merge-prep report/integration manifest:

`<B_INTEGRATION_MANIFEST_PATH_AND_SHA>`

Formal archives and hashes are frozen in the master contract.

### Worktree/branch rule

Do not use either old A or B worktree for integration.

Create clean independent worktrees for:

- Framework `hrl/vm-llm-m4b-v0` from `<A_INTEGRATION_HANDOFF_SHA>`;
- Core `hrl/vm-llm-m4b-v0` from
  `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`.

Before edits record:

- `git status --short`;
- local HEAD;
- remote branch existence;
- remote A/B source SHAs;
- submodule/Core linkage used by Framework;
- disk capacity for selective trace staging.

The Core branch initially contains **no semantic change** relative to accepted
M1-M3.

Acceptance I0:

- clean worktrees;
- exact source SHAs;
- no untracked generated simulation output except pre-existing explicitly
  documented files;
- no B Core imported.

---

## I1 — deterministic path-scoped Track-B import

Do not run a wholesale `git merge` of Track B.

Use exact source `<B_ACCEPTED_FRAMEWORK_SHA>` and import only B-owned files
listed in the accepted merge-prep integration manifest.

Expected families:

```text
docs/vm_tlb/llm/**
docs/vm_tlb/review_packs/M4A_*/**
docs/vm_tlb/codex_handoff/m4a/**
docs/vm_tlb/chatgpt_handoff/M4A_*.md
docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_*.md
util/llm_trace_capture/**
reviewed M4A NVBit tracer ROI source changes
```

Do not import B copies of:

```text
docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/CODEX_NEXT_STAGE.md
```

Do not overwrite current M1-M3 review packs or Track-A stage specs.

Create:

`docs/vm_tlb/review_packs/M4I_AB_INTEGRATION/B_IMPORT_MANIFEST.tsv`

with at least:

```text
path
source_B_sha
source_blob_sha
destination_blob_sha
category
reason
```

For every imported source file, `source_blob_sha == destination_blob_sha` until
an explicitly separate integration edit modifies it.

Run `git diff --check` before committing the import.

Acceptance I1:

- path list is explicit and reviewable;
- no stale B current-state handoff takes control;
- M1-M3 files remain byte-identical unless a new integrated handoff file is
  intentionally added later;
- B capture/merge-prep provenance is preserved.

---

## I2 — immutable formal artifact binding

Never edit or repack the two accepted formal archives.

Reverify on the integration host:

- archive file exists;
- external SHA256 equals frozen value;
- `zstd -t`/equivalent integrity;
- tar listing;
- internal `SHA256SUMS`;
- workload manifest;
- allocation sidecar;
- semantic kernel manifest from accepted merge-prep;
- semantic full/compute-only/NCCL-only list hashes;
- address-coverage JSON and hashes if merge-prep produced them.

Create an integration-local artifact lock, e.g.:

`docs/vm_tlb/review_packs/M4I_AB_INTEGRATION/FORMAL_ARTIFACT_LOCK.md`

The lock must bind:

- prefill archive path/SHA;
- decode1 archive path/SHA;
- capture source SHA;
- model/revision;
- semantic manifest/list SHAs;
- sidecar/manifests inside each archive;
- merge-prep coverage artifact SHAs;
- semantic-classifier/decoder source SHAs.

### Selective staging

Create a non-Git scratch root whose name includes the archive SHA prefix.

Extract only what integrated replay needs, preferably retaining compressed
`*.traceg.xz` files rather than materializing plaintext traces.

Minimum staged content per ROI:

```text
workload-manifest.json
allocation-sidecar.json
semantic kernel manifest
full kernelslist derivative
compute-only kernelslist derivative
NCCL-only kernelslist derivative
traces/*.traceg.xz required by the selected lists
```

If a derivative list references a file absent from the frozen archive/stage,
STOP.

Acceptance I2:

- archive hashes reverified;
- staged input derivation fully reproducible;
- no mutation of frozen archives;
- no plaintext full-trace expansion required.

---

## I3 — final Core / Framework build integration

Point the new Framework integration branch at the new Core integration branch,
which must still be semantically identical to accepted Track-A Core at this
point.

Perform a **cold** build.  Do not reuse an ABI-stale binary built against a
different Core header/layout.

Rerun a compact frozen M1-M3 admission set before touching LLM behavior:

- M1 disabled/ideal transparency;
- M2 pending waiter retry directed test;
- G3 lookup no-polling directed test;
- PTE physical/non-recursive association test;
- PWC directed test;
- one-kernel LUD functional/real replay;
- one bounded BFS VM replay or accepted equivalent.

Acceptance I3:

- build PASS;
- no M1-M3 regression;
- final Core SHA lineage is from `5ba17a1b...` only;
- no LLM-specific code has yet altered VM semantics.

---

## I4 — formal trace address-domain and metadata audit

This gate decides whether paper-specific 49-bit mode can be used without
rewriting trace addresses.

Use the exact semantic full trace inputs and exact address decoder accepted from
merge-prep.

For **all decoded memory references** in both prefill and decode1 record:

- minimum address;
- maximum address;
- maximum used bit index / minimum required unsigned VA width;
- count with address `>= 2^49`;
- count with address `>= 2^56`;
- whether any requested byte interval crosses configured width;
- upper-bit pattern histogram for references above `2^49` if any.

Do not mask, canonicalize or truncate.

### Decision

If every valid reference lies in `[0, 2^49)`:

- authorize 49-bit mode for paper-facing M4C/M4B runs;
- keep 56-bit generic mode as a diagnostic cross-check.

If any legitimate reference requires >49 bits:

- generic 56-bit replay may continue for compatibility/characterization;
- **paper-specific Segmentation must STOP** before descriptor implementation,
  unless a later ChatGPT handoff explicitly approves a trace-address relocation
  contract.

A simple `addr & ((1<<49)-1)` is forbidden.

### Metadata consistency

Using the accepted runtime sidecars and merge-prep coverage outputs, verify:

- exactly one formal rank0 contiguous Weight allocation per ROI;
- Weight range is within trace address domain;
- KV ranges used for each ROI follow the merge-prep temporal contract;
- no unexpected Weight/KV overlap;
- no synthetic KV;
- sidecar range endpoints are overflow-safe;
- trace-side coverage is nonzero where merge-prep says it is nonzero.

Record both object-reference and object-byte coverage, but do not require 100%
coverage: activations/workspaces remain legitimately `UNKNOWN` unless captured
metadata identifies them.

Acceptance I4:

- exact address-domain result known;
- paper 49-bit eligibility explicitly PASS or BLOCKED;
- Weight segment candidate range frozen;
- no metadata ambiguity needed by M4B.

---

## I5 — semantic list and parser compatibility on final Core

Track B's old parser smoke is evidence only.  Repeat compatibility on the final
integrated Core/Framework.

For each ROI and each semantic class present:

### COMPUTE

Select representative:

- early;
- middle;
- late;
- distinct kernel-name families;
- high-memory-traffic kernel when identifiable from trace metadata/statistics.

### NCCL

If present, test at least one sample from each observed semantic NCCL family.

### MEMCPY / UNKNOWN

Inspect/test if present; do not silently discard.

For each sample prove:

- compressed trace opens;
- header parses;
- trace instruction parser starts;
- simulator binds launch dimensions/register/shared-memory metadata;
- no unsupported address format;
- no immediate unsupported opcode/format error;
- M1-M3 VM disabled/ideal/functional entry does not corrupt parser state.

Compatibility failure of an NCCL kernel does **not** invalidate the capture.
Record it as evidence for trace-policy selection.

Acceptance I5:

- all compute families needed for formal replay are compatible;
- any NCCL incompatibility is fully identified;
- no trace has been rewritten to make parser smoke pass.

---

# M4R — replay compatibility and trace-policy gate

## R0 — build exact launch manifests

For each ROI create immutable integration launch manifests for:

- `FULL_RANK0`;
- `COMPUTE_ONLY_TP_PARTITION`;
- `NCCL_ONLY_DIAGNOSTIC` if NCCL exists.

Each launch manifest records:

- source archive SHA;
- semantic manifest SHA;
- list SHA;
- number of list entries;
- counts by semantic class;
- integrated Framework/Core SHAs;
- exact simulator config SHA;
- exact command.

Do not call compute-only a raw capture; it is a non-destructive derivative.

---

## R1 — controls on bounded representative traces

For representative compute kernels run:

1. `CONTROL_VM_DISABLED`;
2. `CONTROL_VM_IDEAL_IDENTITY`;
3. `GENERIC_M3_LLM_BASELINE`.

Required checks:

- disabled vs ideal retains expected non-translation behavior;
- functional/real translation makes progress;
- final translation state quiesces;
- no duplicate data/store/atomic effect;
- no PTE recursion/misassociation;
- raw SimVA preserved.

For at least one kernel with meaningful memory pressure, require nonzero TLB
statistics so an accidentally bypassed VM hook cannot pass.

---

## R2 — full-list bounded throughput pilot

Before a long formal ROI replay, run an exact-config bounded pilot whose only
purpose is to estimate full replay feasibility.

Record:

- wall time;
- simulated instructions/cycles;
- kernels completed;
- trace bytes consumed;
- resident memory;
- simulator instructions/second or kernels/hour;
- projected full-ROI time.

No source/config tuning may be performed from performance results at this gate.

If progress is healthy, continue even if slow.  If there is no progress under
`AGENTS.md` timeout rules, STOP with the exact kernel/state.

---

## R3 — trace-policy evidence

If semantic NCCL count is zero, `FULL_RANK0` and compute-only may legitimately
be identical; prove hashes/counts.

If NCCL count is nonzero:

- preserve `FULL_RANK0` as immutable self-capture fidelity path;
- preserve `COMPUTE_ONLY_TP_PARTITION` as one-partition compute derivative;
- record instruction/kernel/memory-reference share attributable to NCCL where
  obtainable without changing simulator semantics;
- compare bounded execution behavior of both.

The target paper says TP factor 4 and simulation of one partition but does not
publish its collective-kernel treatment.  Therefore M4R does not label either
path `PAPER_EXACT`.

Unless the future authorization says otherwise, the default planned policy is:

- use `COMPUTE_ONLY_TP_PARTITION` for primary paper-facing translation
  characterization because it most directly represents a single compute
  partition;
- retain `FULL_RANK0` as required self-capture sensitivity/provenance path;
- report both when NCCL materially changes translation traffic.

If B merge-prep reveals evidence that invalidates this planned policy, ChatGPT
must update the authorized start before execution.

---

## R4 — replay compatibility closeout

M4R passes when:

- integrated final Core parses and executes the required compute trace path;
- formal launch manifests are frozen;
- 49-bit eligibility is known;
- primary and sensitivity trace policies are explicitly labeled;
- throughput feasibility is measured;
- no M1-M3 regression exists.

Create:

`docs/vm_tlb/review_packs/M4R_LLM_REPLAY_COMPAT/`

and automatically continue to M4C if every gate passes and no hard-stop
condition is encountered.
