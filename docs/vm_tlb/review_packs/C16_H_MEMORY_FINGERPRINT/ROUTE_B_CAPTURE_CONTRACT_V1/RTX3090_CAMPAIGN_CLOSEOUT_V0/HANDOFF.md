# C16 Route-B RTX3090 Campaign Closeout — Handoff V0

## 0. Purpose

This branch is a **data closeout / curation branch** for the completed RTX3090 C16 Route-B campaign.

The immediate objective is **not** to resume GPU experimentation and **not** to repair the two unresolved CUTLASS identity rows. The objective is to turn the already collected RTX3090 evidence into a compact, auditable, provenance-preserving research dataset that can be reused for later Cache/TLB/AI-workload analysis.

This V0 handoff authorizes **inventory, classification, manifest generation, deterministic summarization, and cleanup planning only**.

No destructive cleanup is authorized in V0.

---

## 1. Repository / branch authority

Repository:

```text
https://github.com/swayhrl/accel-sim-framework.git
```

Closeout working branch:

```text
hrl/vm-c16-g-3090-campaign-closeout-v0
```

Branch base / operational handoff HEAD:

```text
dac65d53ff16c5919462f05a354be6fe9a4500c7
```

V12.8 offline science authority remains immutable:

```text
cbc63026651abb0715a29918915a77726c57b976
```

Frozen G1 scientific authority remains immutable:

```text
branch: hrl/vm-c16-g-retry570-v0
commit: ef0d89b1ce297518f86c51cddce190abd47e7364
```

Recovery authority remains immutable:

```text
branch: hrl/vm-c16-g-post-restart-recovery-v12-6
commit: 62428f2cea9ed4cd2def11339311d4347282d9c7
```

Do not rewrite or reinterpret those authorities from this closeout branch.

---

## 2. Frozen RTX3090 campaign facts

Runtime identity:

```text
GPU: RTX 3090
Driver: 570.124.04
CUDA: 12.4
PyTorch: 2.5.1+cu124
Transformers: 4.57.6
NVBit: 1.7.5
```

Frozen Llama identity:

```text
model: meta-llama/Llama-3.2-1B
revision: 4e20de... (use the exact revision already recorded by the authority artifacts; do not shorten it in generated manifests)
prompt: The capital of France is
input shape: [1, 6]
dtype: fp16
execution: eager
max_new_tokens: 4
```

Current scientific state:

```text
Q1                         PASS
Q2 prefill                 COMPLETE
Q2 decode                  COMPLETE
Route-A -> Q2 bridge       PASS
V2 static map              34 / 36 exact
CUTLASS unresolved         2 / 36
representative canary      NOT_AUTHORIZED
formal capture             NOT_AUTHORIZED
```

The two unresolved V2 rows remain failed closed:

```text
FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED
```

Do not shrink denominators, infer module ownership, fabricate static MREF mappings, or upgrade these rows during closeout.

---

## 3. Closeout principles

The closeout must preserve four distinct layers:

1. **AUTHORITATIVE** — raw or frozen evidence that defines scientific facts.
2. **DERIVED** — deterministic outputs traceable to authoritative inputs and producer code.
3. **ARCHIVAL_ONLY** — useful historical/debug evidence that is not current authority.
4. **SUPERSEDED** — older outputs replaced by a clearly identified later authority.

If an item cannot be classified confidently, mark it:

```text
UNKNOWN_REVIEW_REQUIRED
```

Never guess.

For every file considered authoritative or derived, preserve or recover as much provenance as possible:

```text
path
size
sha256
mtime if available
origin run / phase
prefill or decode
producer script
producer git commit
input dependencies
scientific status
superseded-by relation if any
notes
```

Do not modify the bytes of authoritative raw evidence.

---

## 4. Target logical dataset layout

The final curated dataset is expected to converge toward this logical organization:

```text
c16_rtx3090_campaign/
├── 00_manifest/
├── 01_raw_authority/
├── 02_derived_authority/
├── 03_analysis_products/
├── 04_failed_and_debug/
└── 05_docs/
```

This is a **logical target**, not authorization to move files in V0.

Expected manifest / documentation products eventually include:

```text
CAMPAIGN_MANIFEST.yaml
FILE_MANIFEST.csv
SHA256SUMS
RUNTIME_ENV.md
AUTHORITIES.md
DATA_DICTIONARY.md
README.md
3090_CAMPAIGN_FINAL_STATE.md
DATASET_LAYOUT.md
SCIENTIFIC_AUTHORITY.md
KNOWN_LIMITATIONS.md
RTX3090_TO_RTX4080_HANDOFF.md
REPRODUCTION_AND_ANALYSIS_GUIDE.md
```

---

## 5. V0 scope — authorized work only

### 5.1 Inventory

Build a complete inventory of RTX3090 C16 Route-B artifacts that are accessible from the current repository/worktree and any already-configured local archive paths.

Search systematically for:

- Q1 evidence
- Q2 prefill evidence
- Q2 decode evidence
- Route-A evidence
- Route-A -> Q2 bridge products
- V2 static maps
- CUTLASS identity evidence
- qualification evidence
- recovery / copyback evidence
- runtime/environment receipts
- model identity receipts
- analysis products
- debug outputs
- superseded copies
- duplicate copies
- temporary files

Do **not** assume that every historical file still exists locally. If an expected authority is represented only by committed summaries/receipts, record that explicitly rather than inventing a path.

### 5.2 Classification

Classify each inventoried artifact as one of:

```text
AUTHORITATIVE
DERIVED
ARCHIVAL_ONLY
SUPERSEDED
UNKNOWN_REVIEW_REQUIRED
```

Also assign, where possible:

```text
campaign = RTX3090
phase = Q1 | Q2_PREFILL | Q2_DECODE | ROUTE_A | BRIDGE | V2 | RECOVERY | ENV | ANALYSIS | DEBUG | OTHER
role = RAW | RECEIPT | SUMMARY | SCRIPT_OUTPUT | LOG | DEBUG | TEMP | OTHER
```

### 5.3 Hash / duplicate analysis

For every accessible regular file in scope:

- record size;
- compute SHA256 unless doing so would be unreasonable for a very large file; if skipped, record why;
- group exact duplicate SHA256 values;
- distinguish duplicate bytes from merely similar filenames;
- estimate disk usage by category;
- identify obvious redundant copies and temporary artifacts.

Do not delete duplicates in V0.

### 5.4 Authority reconciliation

Cross-check repository evidence against the frozen authority commits above.

At minimum confirm that the closeout report preserves these facts:

- Q1 PASS;
- Q2 prefill/decode COMPLETE;
- Route-A -> Q2 bridge PASS;
- V2 static map = 34/36 exact;
- two CUTLASS rows remain failed closed;
- representative canary and formal capture remain unauthorized;
- recovery/copyback status remains closed as already documented.

If a contradiction is found, stop classification of that item and mark `UNKNOWN_REVIEW_REQUIRED`; do not silently reconcile it.

### 5.5 Deterministic summaries

It is permitted to generate **new summaries from existing evidence** provided that:

- no GPU program is executed;
- the transformation is deterministic;
- inputs are recorded;
- producer script and commit are recorded;
- outputs are clearly marked DERIVED or ANALYSIS_PRODUCT, not raw authority.

Useful summary candidates include:

```text
WORKLOAD_SUMMARY.csv
PHASE_SUMMARY.csv
KERNEL_SUMMARY.csv
STATIC_DYNAMIC_BRIDGE.csv
MEMORY_ACCESS_SUMMARY.csv
PAGE_FOOTPRINT_SUMMARY.csv
CACHELINE_REUSE_SUMMARY.csv
TLB_RELEVANT_SUMMARY.csv
```

However, V0 priority is inventory/provenance. Do not invent a table merely to satisfy this list if current evidence is insufficient.

### 5.6 Cleanup planning only

Create a cleanup proposal, but do not execute it.

Candidate categories may include:

- duplicate byte-identical copies;
- build products;
- caches;
- obvious temporary grep/sed outputs;
- redundant stdout copies;
- superseded generated summaries;
- abandoned debug scratch files;
- core dumps.

For every proposed removal, record:

```text
path
size
sha256 if available
reason
classification
why removal cannot affect authority/provenance
```

No file deletion, move, rename, compression, or destructive rewrite is authorized in V0.

---

## 6. Explicitly forbidden in V0

Do **not**:

```text
run any GPU workload
run Llama
run Q1
run Q2
run Route-A capture
repair CUTLASS code-object identity
open representative selection
run representative canary
run formal capture
change the frozen runtime contract
change model revision or input
shrink selection denominators
reinterpret unresolved rows as PASS
mix RTX4080 evidence into RTX3090 authority
move/delete/rename existing evidence
rewrite authoritative raw files
force-push or rewrite frozen branches
```

If a command might start a CUDA workload, do not run it.

CPU-only parsing, hashing, repository inspection, and deterministic analysis of existing files are allowed.

---

## 7. RTX4080 separation rule

RTX4080 work is a separate campaign/lane.

Do not merge or use RTX4080 outputs to fill gaps in RTX3090 evidence.

The future relationship should be:

```text
C16 / RTX3090
  -> frozen curated dataset

C16 / RTX4080
  -> independent runtime campaign

comparison
  -> performed only after both lanes have explicit provenance
```

If RTX4080 files are encountered during inventory, exclude them from the RTX3090 dataset and record the exclusion.

---

## 8. Required V0 deliverables

Create a closeout directory under this handoff directory and produce at least:

```text
V0_INVENTORY/
├── 3090_CAMPAIGN_FINAL_STATE.md
├── FILE_INVENTORY.csv
├── CLASSIFICATION_SUMMARY.md
├── DUPLICATE_AND_DISK_USAGE_REPORT.md
├── DATASET_CURATION_PLAN.md
├── DELETE_CANDIDATES.md
├── UNKNOWN_REVIEW_REQUIRED.md
└── INVENTORY_METHOD.md
```

Optional helper scripts should live under an appropriate `util/vm_tlb/c16/...` path, not inside the evidence directory, and must be deterministic and CPU-only.

### `3090_CAMPAIGN_FINAL_STATE.md`

Must clearly separate:

- frozen scientific facts;
- accessible raw evidence;
- accessible derived evidence;
- missing/external-only evidence;
- known limitations;
- unresolved CUTLASS rows;
- what remains intentionally not authorized.

### `FILE_INVENTORY.csv`

Recommended columns:

```text
path,size_bytes,sha256,classification,campaign,phase,role,prefill_decode,authority_commit,producer,producer_commit,superseded_by,notes
```

Use blank/UNKNOWN fields rather than guessed metadata.

### `DELETE_CANDIDATES.md`

This is proposal-only. The report must end with an explicit statement:

```text
NO FILES WERE DELETED, MOVED, RENAMED, COMPRESSED, OR REWRITTEN IN V0.
```

---

## 9. V0 execution procedure

1. Verify current branch and HEAD.
2. Read this handoff fully.
3. Read the existing V12.8 decision/closeout/bridge/recovery authority documents needed to understand provenance.
4. Inspect current repository/worktree and accessible archived evidence.
5. Build inventory without changing evidence.
6. Classify conservatively.
7. Hash and deduplicate logically.
8. Generate the required V0 reports.
9. Run CPU-only self-checks on generated manifests/reports.
10. Review `git diff` carefully for accidental evidence changes.
11. Commit only new closeout reports/scripts/docs.
12. Push the closeout branch.
13. Report results to the user for review.

Do not proceed to physical data reorganization or deletion after the V0 report. Await explicit review/authorization.

---

## 10. Required Codex final report

At the end of V0, report succinctly:

1. branch and final commit;
2. exact files added/changed;
3. number of inventoried files and total bytes;
4. counts by classification;
5. duplicate-byte groups and reclaimable bytes estimate;
6. major authority paths found;
7. expected authority artifacts not locally accessible;
8. all `UNKNOWN_REVIEW_REQUIRED` items;
9. proposed delete candidates and total proposed bytes;
10. confirmation that no GPU workload ran;
11. confirmation that no existing evidence was moved/deleted/renamed/rewritten;
12. recommended V1 physical curation actions, but do not execute them.

---

## 11. Stop conditions

Stop and report rather than improvising if any of the following occurs:

- current branch/head is not the expected closeout branch lineage;
- repository state contains unexpected uncommitted modifications to scientific evidence;
- an authority contradiction cannot be resolved from committed evidence;
- a requested step would require running CUDA/GPU code;
- safe classification would require guessing provenance;
- a cleanup action would require deleting/moving evidence.

The closeout should prefer an explicit unresolved item over an unjustified inference.
