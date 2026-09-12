# C16-G Wave-1 runtime status

Status: `C16_G_AUTODL_WAVE1_RUNTIME_ACTIVE`  
Publication policy: `REMOTE_CHECKPOINT_POLICY.md` at read-only handoff commit
`9938b59ab80e6d1c77cc1efa6f6980e4cdfac5bc`.

## Runtime anchors

| Field | Value |
|---|---|
| Formal standalone runtime source commit | `3f02eef6e0d00ea654821be8539bb82f463e87e5` |
| Direct-semantic runtime source commit | `b241fecfe5cd78bc2cdbb733e3a437d68b741c89` |
| Current G publication head before this checkpoint | `f7d1c2cb4d41b26472893a7d23466402c8e92e70` |
| P3 AWQ native runtime source commit | `07575b6d1abc42f68414a8b0ad27c0a6d7d38e66` |
| Meaning of P3 AWQ source commit | Focused-test-passed explicit `AutoAWQ.from_quantized` load only: `fuse_layers=false`, `device_map=cuda:0`, no offload, exact frozen sequence length.  It does not alter completed P0/P1 scientific receipts. |
| Formal standalone path | The only scientific performance path.  All rows below were run without CPU offload and with the frozen `float16` / eager / SDPA binding. |

`3f02eef6` is the immutable source anchor for the completed P0/P1 formal runs.  A
future source or contract change that affects a scientific run must pass focused
tests, be committed and pushed, and be named in that run's receipt before use.

## Direct semantic evidence (non-timing)

Llama S2 run `cd3e40be-a7d5-43e5-9030-d84dc158f406` passed direct module-NVTX
instrumentation and stable kernel/correlation/stream join qualification under
runtime source `b241fecf…`.  Its only status is
`SEMANTIC_DIAGNOSTIC_ONLY` / `NOT_FOR_NATIVE_TIMING`; both native runtime and
Nsight receipts set scientific eligibility false.  It has 20,669 direct,
unambiguous mappings, 24,611 conservative `UNKNOWN` rows, and zero ambiguous
direct-range ties.  The full map remains outside Git; the consumer-facing small
coverage table, receipt, and exact external artifact hashes are in
[`direct_semantic_s2`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/direct_semantic_s2/).

The initial direct-semantic run `7c9d0ba8-2376-46f9-9791-2c3b8c8fb260` remains
in the ledger as `NON_SCIENTIFIC_DIAGNOSTIC` after an NVTX hook-return bug.  The
corrected source was focused-test-passed and pushed before the successful new
run.  Neither diagnostic changes G0/G1 or the standalone scientific path.

Qwen2.5-0.5B S2 run `1a748d40-8144-47f3-93f6-4b8e75be4e65` also passed
direct-semantic qualification: 33,184 direct/unambiguous rows, 37,040
conservative `UNKNOWN` rows, and zero direct-range ties.  It is a separate
non-timing diagnostic.  Its map never joins absolute timestamps to a different
run's clean census; Lane P alone may reconcile runs through its
`EVENT_INPUT_CONTRACT`.  Its semantic publish-manifest SHA256 is
`b9a0a3aea01887f58877ecadd4d119582e09387702122be0ff4564b918d3d5fb`;
consumer-facing coverage/receipt/hash index is in
[`direct_semantic_qwen05_s2`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/direct_semantic_qwen05_s2/).

## Consumed package checkpoints

| Package | Fixed A commit | Manifest SHA256 | Consumption state |
|---|---|---|---|
| `C16_GPU_PACKAGE_P0` (Llama 3.2-1B) | `20fb38e6ca629f1a93db7939248bd1a03790724c` | `ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f` | Previously hash-closed and used for the formal Llama standalone set. |
| `C16_GPU_PACKAGE_P1` (Qwen2.5-0.5B) | `4e73a1d0f435ba4d1dae1a9e749b8b82e54b7f63` | `d8ac3ca44c4344b9a5fa752ba5a6549c007e901b26b426c9713b4d7e8749eb84` | Hash-closed before execution.  Transfer receipt SHA256: `bfa4e7a625fef437c7a2c131681c14f3c0e182cb403be23c6938ff3d11bfacf1`. |
| `C16_GPU_PACKAGE_P3` Qwen2.5-7B AWQ | `168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d` | `704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c` | Immutable A release verified read-only.  Next authorized package: transfer/hash-close P3 after this semantic checkpoint. |
| `C16_GPU_PACKAGE_P2` Qwen2.5-7B raw | `168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d` | `c937590dd4ea2b4f6407db7d8b077ed263af3cbc14562ef34142aa834b133f26` | Immutable A release verified read-only.  Consume only after the P3 AWQ G0 -> standalone baseline -> G1 group. |

## Qualified execution state

| Deployment / group | G0 | G1 | G2 | G3 | Latest completed formal group |
|---|---|---|---|---|---|
| Llama 3.2-1B P0 | PASS | PASS: S0/S1/S2, then S3/S4 bounded full-range Nsight census | Pending fixed target | Pending fixed target | S4 standalone baseline plus G1 (`da75b6e2-5f58-4f6c-9cc8-131180013dfa`) |
| Qwen2.5-0.5B P1 | PASS (`67dea9e7-29f9-488a-b70d-e345508f3f79`) | PASS: S1 (`2ec7d963-228d-4c8a-bcfa-60c895f13b88`) and S2 (`bbe3ef73-bdca-443d-8fa6-58b59a35ca4c`) | Pending fixed target | Pending fixed target | S2 standalone baseline plus G1; this is a meaningful completed standalone model/scenario group. |

The first malformed Qwen S1 Nsight invocation (`baa55265-4b7b-4dd8-aed6-6fcc6abca148`)
has a retained ledger entry marked `NON_SCIENTIFIC_DIAGNOSTIC`; it has no raw
profile and is excluded from baseline/census.  Parent/child lease proof remains
mandatory, so neither that diagnostic nor a child invocation can bypass or
double-count the budget.

## Resident decision

`RESIDENT_MODEL_NO_GO_WITH_EVIDENCE` remains in force.  Q1 failed its strict
scenario-cleanup envelope check and all associated historical ledger rows remain
`NON_SCIENTIFIC_DIAGNOSTIC`.  Record additionally:

`RESIDENT_REQUALIFICATION_DEFERRED`

There will be no Q2 or other resident GPU work in this window.  Resident mode is
not an alternative scientific path and does not alter the qualified standalone
baseline, census, profiler, NCU, or NVBit methods.

## Raw-artifact index and next queue

The returned `.nsys-rep` artifacts, including the retained semantic diagnostic
raw, are indexed by immutable
path/size/SHA in [RAW_ARTIFACT_INDEX.tsv](RAW_ARTIFACT_INDEX.tsv).  They are not
Git payloads.  Each listed local copy has an independently verified SHA256; the
remote copies were still present at this checkpoint and may be reclaimed only
after the published index is available and the corresponding local digest is
reconfirmed.

Llama's direct-semantic `.nsys-rep` and temporary remote SQLite were reclaimed
from AutoDL only after their published local SHA256 confirmations.  Qwen0.5's
matching raw remains remote at this checkpoint; both entries give the local
hash-closed retained copy, and their small remote receipts remain available.

Next authorized GPU task: transfer and full hash-close P3 AWQ from A's fixed
`168c9714…` release, publish that consumption checkpoint, then run standalone
Qwen7-AWQ G0 -> baseline -> G1.  Next is the analogous P2 raw group.  Package
transfer occurs between measurement groups, never during one, and Lane P's
local semantic merge is not a prerequisite for this queue.

## Known capability / analysis boundaries

- G2/G3 have no frozen target and cannot gate G0/G1.
- Existing nsys raw is retained losslessly outside Git.  Remote export is not the
  default catalog path; raw -> remote SHA -> local transfer -> local SHA -> local
  export is the policy path.
- Direct runtime semantic evidence is a separately marked diagnostic effort.  It
  may not overwrite any qualified timing row or alter the meaning of the clean
  P0/P1 census.  Local nsys 2022.4.2 cannot parse remote nsys 2024.1 reports;
  the S2 semantic SQLite was a one-time remote-export fallback, never a remote
  launch TSV/catalog.
- P3 AWQ native execution is bound to `07575b6…`, which has a no-GPU focused
  test for the exact AutoAWQ loader and CUDA-residency contract.  The remote
  runtime is updated only from that immutable pushed source before P3 G0.
