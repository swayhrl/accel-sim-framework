# CODEX Goal — 174-new Repo + Shared-Storage Inventory

## Role

Run on the new analysis Docker:

```text
ssh root@10.208.130.174 -p 2239
```

This task inventories the code/config/document authority already available in Git and the historical filesystem material currently visible through shared mounts. It does not reinterpret old scientific results without source evidence.

## Goal

Establish the 174-new side of C12–C15 inheritance so that, after joint review with the old174 archaeology pack, 174-new can become the sole long-term owner of historical simulator analysis and can connect new C16 traces to the same TLB/Cache workflow.

## Hard safety constraints

- CPU-only / filesystem-only.
- Do not run GPU/model/NVBit/NCU/NSYS workloads.
- Do not rerun long historical simulations in this round.
- Do not mutate current C16 formal raw under node164.
- Do not delete/move/rename historical shared data.
- Do not copy large old174 assets preemptively.
- Do not modify ChatGPT-owned handoff files.
- Do not infer that a result is FORMAL merely because a file name says `final`.

## A. Git-side inventory

Inventory historical simulation-related repository assets under at least:

```text
configs/vm_tlb/
util/vm_tlb/
docs/vm_tlb/
```

Search for C12–C15 and related concepts/aliases:

```text
C12 C13 C14 C15
c12_c5
m4b m4c
TLB PTW Segment Selective Cache L1 L2
replay finalize checkpoint
```

For each relevant Git artifact record:

```text
path
purpose/stage
file type (config/script/analyzer/doc/review-pack)
latest relevant commit known locally
whether executable/current/legacy
known inputs
known outputs
hard-coded paths/host assumptions
recommended inheritance status
```

Classify code/config as:

```text
REUSE
REVALIDATE
REFERENCE_ONLY
OBSOLETE
UNKNOWN
```

Do not modify implementation in this round unless needed for a tiny read-only inventory helper.

## B. Historical docs / review-pack inventory

Identify repository documents that record previous C12/C13/C14/C15 results, especially:

- stage status / closeout documents;
- review packs;
- result CSV/TSV/JSON tracked in Git;
- source anchors / commit histories;
- formal-vs-diagnostic boundaries;
- known bugs/fixes that affect result validity.

Create a map from documented conclusions to the artifact names/paths that supposedly support them. Mark unsupported links `UNRESOLVED_DOCUMENT_REFERENCE`.

## C. Shared filesystem visibility inventory

Read-only inventory currently visible historical data under:

```text
/root/share
/root/data
```

and the canonical node164 root:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Do not assume old174 paths that are not visible.

For C12–C15-related candidate directories/files visible here, record:

- absolute path;
- bytes/file count;
- representative/key SHA256;
- apparent role;
- whether already represented in node164 historical provenance;
- whether duplicate of another shared path;
- whether current analysis code can consume it as-is.

## D. Current simulator capability inventory

Without launching a long simulation, determine the current code-level entry points needed to replay historical or new traces:

```text
trace conversion/replay
config selection
simulator invocation wrapper
TLB/PTW statistics extraction
Segment / Selective analysis
Cache statistics extraction
post-processing / finalize
```

For each, document expected input format and output format.

The purpose is to answer whether the current repo already contains a runnable path from a cataloged trace to a TLB/Cache result, and where compatibility gaps remain.

## E. Current C16 integration points

Document how the current 174-new C16 pipeline could eventually feed simulator analysis:

```text
C16 formal raw / derived fingerprint
  -> what conversion is required?
  -> what simulator trace format is required?
  -> what semantic information is lost/preserved?
  -> which metrics can be compared directly to historical C12–C15?
```

Do not implement a new conversion yet unless a trivial existing path already works. This round is inventory and interface definition.

## Required deliverables

Create:

```text
docs/vm_tlb/review_packs/C12_C15_174NEW_REPO_SHARED_INVENTORY_V1/
├── README.md
├── GIT_SIMULATION_ASSET_INVENTORY.tsv
├── CONFIG_INVENTORY.tsv
├── ANALYZER_AND_REPLAY_INVENTORY.tsv
├── HISTORICAL_DOC_RESULT_MAP.tsv
├── SHARED_VISIBLE_ASSETS.tsv
├── CURRENT_SIMULATION_ENTRYPOINTS.md
├── C16_TO_SIMULATOR_INTERFACE_GAPS.md
├── OPEN_QUESTIONS.md
└── SHA256SUMS
```

Also update a Codex-owned report:

```text
docs/vm_tlb/codex_handoff/c16/simulation_inheritance/174NEW_REPO_SHARED_INVENTORY_REPORT.md
```

## Minimum acceptance criteria

The review pack must let ChatGPT answer:

1. Which C12–C15 configs/scripts/analyzers are already safely inherited through Git?
2. Which historical result documents/review packs are still available in Git?
3. Which old filesystem artifacts are already visible through shared storage from 174-new?
4. Which current simulator entry points are runnable today versus legacy/reference-only?
5. What exact interface gap remains between current C16 formal traces/derived data and historical simulator analysis?
6. What should be revalidated in Round 2 instead of blindly trusted?

## STOP condition

STOP after Git/shared-storage inventory, review-pack hash closure, clean Git status and push.

Do not perform large-file migration or long simulator replay in this round.
