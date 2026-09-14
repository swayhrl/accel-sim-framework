# C16 Data Pipeline Parallel Execution Plan V1

Date: 2026-09-14
Ownership: ChatGPT

## Objective

Close the 109 -> 174-new -> 164 data plane quickly while preserving scientific provenance. Minimize coordination rounds by running independent producer- and ingest-side work in parallel, then combining cross-node qualification, legacy import, and catalog seeding into one integration round.

## Frozen topology

```text
109 / RTX4080
  producer / GPU capture

174-new / 2239
  ingest / verification / CPU analysis

164
  long-term raw + derived data plane

GitHub
  code / schemas / manifests / receipts / review packs

old174 / 2233
  historical source only after OLD174_HANDOVER_COMPLETE
```

## Round 0 — already running + immediate parallel work

### 174-new

Finish current Phase B only:

```text
164 data-root admission
namespace freeze
filesystem capability audit
catalog V1 seed
STOP
```

### 109 — may start immediately in parallel

Implement producer-side Pipeline V1 locally without contacting 174-new or 164:

```text
RUN_ID generator
RUN_MANIFEST schema support
capture staging/ready/transferred/quarantine state machine
finalize_capture
publish dry-run / transport preparation
ACK verifier
non-destructive cleanup policy
synthetic local fixture tests
```

No scientific capture rerun is required.

## Round 1 — single integration round after both Round-0 halves PASS

Run 109 and 174-new in parallel against the same frozen contract.

### Step 1: receiver implementation

174-new implements:

```text
receive/verify/admit
TRANSFER_ACK
catalog immutable entry
catalog snapshot rebuild
quarantine/fail-closed paths
```

### Step 2: cross-node data-plane qualification

Use synthetic deterministic data only:

```text
small fixture
64 MiB fixture
1 GiB fixture
partial/resume case
collision/no-overwrite case
source/destination SHA closure
ACK round trip
109 READY -> TRANSFERRED transition
```

If the 1 GiB fixture is materially slow but all semantics pass, a bounded >=256 MiB medium fixture is acceptable only with explicit throughput measurement and filesystem limitation classification.

### Step 3: real legacy import in the same round if Step 2 PASS

Without rerunning scientific workloads:

```text
A. Import RTX4080 clean R5 existing artifacts from node109.
B. Import the curated RTX3090 historical minimum comparison set from old174 source to 164.
C. Register both in the catalog with distinct producer/campaign/scientific-status identities.
D. Import small model/input authority metadata needed for joins.
```

No full recovery-root copy.

## Round 2 — multi-model capture + analysis in parallel

After Pipeline V1 + legacy imports PASS, do not create another infrastructure-only round.

### 109

Begin multi-model capture through the new pipeline:

```text
Qwen2.5-0.5B
Qwen2.5-7B raw where memory-admitted
Qwen2.5-7B AWQ
```

Use existing exact historical bindings. Resource-admit each scenario before capture. Do not force Qwen3-8B or DeepSeek-V2-Lite onto the 16 GiB 4080 when not admitted.

### 174-new

As runs arrive:

```text
verify/admit/catalog
parse NCU/NVBit/NSYS/native
object join
page/cache-line fingerprint
Sampling V2 preparation
cross-model tables
```

Analysis proceeds incrementally; do not wait for all models before parsing the first admitted run.

## Round 3 — only if needed

Reserve a later round only for work that truly cannot be combined:

```text
new prospective input authority for Qwen3-8B / DeepSeek-V2-Lite
larger-GPU capture for models/scenarios not admitted on RTX4080
Qwen3-30B-A3B separate asset/input closure
```

## Efficiency rules

1. Do not rerun already accepted R5 scientific data for infrastructure reasons.
2. Do not make 174-new reproduce CUDA/NCU/NVBit runtime; it is an analysis node.
3. Do not bulk-copy `/root/share/c16_recovery_v3`.
4. Move only curated, hash-closed historical raw needed for comparison.
5. Generate once, verify twice: producer hashes at finalize; destination independently rehashes before admit.
6. No large raw in Git.
7. Keep current and future catalog machine-generated from immutable per-run entries.
8. Automatic continue within a round is allowed only after explicit local gate PASS; otherwise fail closed.

## Final closeout target

Infrastructure is considered complete when:

```text
PIPELINE_V1_END_TO_END_PASS
R5_LEGACY_IMPORT_PASS
RTX3090_MINIMAL_ARCHIVE_PASS
CATALOG_SEEDED_PASS
```

After that, infrastructure work stops being a separate project; all new captures must use the pipeline by default.