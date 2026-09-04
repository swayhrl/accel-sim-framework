# M4A MERGE PREP — offline semantic audit before Track-A integration

Status: **AUTHORIZED NOW — MAIN-SERVER/OFFLINE ONLY**.

This stage prepares the already-captured Route-E LLM artifacts for later integration with the Track-A M1–M3 VM baseline. It must not merge Track A, modify Core VM semantics, recapture GPU data, implement Segmentation, or choose a permanent NCCL keep/drop policy.

## Accepted immutable inputs

Data acquisition is accepted and frozen. Do **not** regenerate or modify either archive.

Capture executable Framework:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Post-capture evidence/report descendant at authorization time:

`f000a8284ee3dc224f89ee3fca6f38c8d8202785`

Model:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Formal prefill archive:

`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`

Expected SHA256:

`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`

Formal decode1 archive:

`/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`

Expected SHA256:

`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`

Frozen parser compatibility anchor used during capture closeout:

`73774727e25fadf89df6f30ef5cf014091115db7`

The capture class remains `PAPER_COMPATIBLE_SELF_CAPTURE`, not author-exact.

## Why this stage exists

The expensive capture is valid, but the post-capture audit exposed two analysis limitations that must be fixed before M4B/integration:

1. `kernelslist.g` stores trace filenames, while the semantic CUDA kernel name is inside each trace header (`-kernel name = ...`). The current filename-only classifier therefore reports NCCL kernels as COMPUTE and the current compute-only derivative is not semantically trustworthy.
2. The current address-coverage analyzer does not decode the tracer's full warp-address format. The tracer emits `list_all`, `base_stride`, or `base_delta` encoding and one memory instruction can contain multiple active-lane addresses. Coverage must decode all active-lane references before Weight/KV/page-footprint claims are allowed.

This stage fixes those offline-analysis issues without changing raw evidence.

# Goal and gates

Run `MP0 -> MP8` as one target. Continue automatically between gates when the current gate passes. Stop only on a defined correctness/provenance blocker.

## MP0 — Admission and immutable-input verification

Before editing code:

- fetch/pull `hrl/llm-trace-prep-v0`;
- verify branch/worktree cleanliness;
- verify both formal archive files exist on the main server;
- independently recompute both archive SHA256 values and require exact match above;
- verify `zstd -t` / tar listing and the existing internal `SHA256SUMS` contract still pass;
- record the exact archive paths and hashes in the new review pack.

A selective staging directory may be used, e.g. `/workspace/m4a-merge-prep/`, but never modify the frozen archives. Do not fully decompress trace text to disk. Extract only the compressed `*.traceg.xz`/needed metadata or stream from the archive.

STOP if either immutable archive fails integrity.

## MP1 — Semantic kernel classifier

Replace/extend the current filename-only classification path so classification is based on the **embedded trace header semantic kernel name**, not the `kernel-*.traceg.xz` filename.

For every `kernelslist.g` entry:

- if the entry is a kernel trace filename, open the corresponding trace/traceg file and read enough header text to obtain exactly one `-kernel name = ...` field;
- if the entry is a `Memcpy...` record, classify the record directly as `MEMCPY`;
- preserve original list order and original raw entry text;
- classify the semantic kernel name as one of:
  - `COMPUTE`
  - `NCCL_COLLECTIVE`
  - `MEMCPY`
  - `UNKNOWN_OTHER`.

NCCL matching must conservatively cover at least the observed `ncclDevKernel_*` forms plus existing collective tokens (`nccl`, `allreduce`, `all_gather`, `allgather`, `reduce_scatter`, `reducescatter`, `broadcast`). Do not label a kernel NCCL only because a trace filename happens to contain a token.

Generate non-destructively for **each ROI**:

- semantic full manifest containing list index, raw list entry, trace path, embedded kernel name, classification and source hashes;
- `compute-only-kernelslist.g` preserving original order but containing only semantic COMPUTE entries;
- `nccl-only-kernelslist.g` as a diagnostic derivative;
- summary counts and unique semantic-name counts;
- reproducible command/provenance record.

Raw/full lists and all trace files remain immutable.

Required tests:

- synthetic fixture whose filename has no `nccl` but whose header is `ncclDevKernel_AllReduce...` must classify as NCCL;
- ordinary compute header must classify COMPUTE;
- Memcpy entry must classify MEMCPY;
- missing/malformed/duplicate kernel-name header must fail or become explicit `UNKNOWN_OTHER`, never silently COMPUTE;
- output ordering and source-entry count conservation must be exact.

Do **not** make the permanent M4B decision to keep or remove collectives.

## MP2 — Formal NCCL inventory

Run the semantic classifier over full formal prefill and decode1.

Record for each ROI:

- total list entries;
- COMPUTE/NCCL/MEMCPY/UNKNOWN counts;
- unique semantic kernel names by class;
- first/middle/last representative names;
- representative NCCL names;
- indices/runs of NCCL entries within the raw ordering;
- source and derivative SHA256 values.

The old `724 COMPUTE / 0 NCCL` and `772 COMPUTE / 0 NCCL` filename-only counts are historical-invalid for semantic interpretation and must be clearly superseded, not silently reused.

## MP3 — Correct trace-address decoder

Replace `analyze_trace_address_coverage.py` with a trace-format-aware streaming decoder, or add a new utility and retire the old regex-only path from formal use.

The formal tracer format must be decoded according to `util/tracer_nvbit/tracer_tool/tracer_tool.cu`:

- read the active/predicate mask encoded in the trace line;
- obtain `mem_width`;
- decode `address_format`:
  - `0 = list_all`;
  - `1 = base_stride`;
  - `2 = base_delta`;
- reconstruct **every active-lane memory address** represented by the instruction;
- never count only the first/base address as if it were the whole warp instruction.

Important source semantics:

- `base_stride` is emitted only when the tracer's active lanes form the supported contiguous constant-stride pattern; reconstruct `popcount(mask)` addresses from base/stride in active-lane order;
- `base_delta` stores the first active address plus deltas between successive active-lane addresses; reconstruct exactly `popcount(mask)` addresses;
- `list_all` contains one explicit address for every active/predicated lane.

Required decoder invariant for every decoded memory instruction:

`decoded_address_count == popcount(active_mask_field)`

unless an explicitly evidenced tracer-format exception is found. Any exception is a STOP/review condition; do not guess.

Required unit fixtures must cover:

- list-all with sparse mask;
- base-stride with multiple lanes;
- base-delta with positive and negative/signed deltas as emitted by the tracer representation;
- one-lane memory access;
- non-memory instruction;
- malformed/truncated record;
- width/page-boundary crossing.

Do not use OCR, pattern inference, or simulator results as a substitute for decoding the recorded format.

## MP4 — ROI-aware Weight/KV range matching

Use the runtime sidecar ranges only as observed provenance. Do not infer tensor identity from access patterns.

Weight matching:

- use the one recorded contiguous rank0 Weight allocation;
- classify a reference as WEIGHT only when its requested byte interval is wholly contained in the observed Weight range.

KV matching must be **ROI-aware**, because each sidecar contains future decode observations as well as the selected ROI:

- for `prefill`, use the `PREFILL step=0` KV observations relevant to the profiled prefill result; exclude later decode-step-2/3 future ranges from prefill classification;
- for `decode1`, use the immediately surrounding observed KV state: `PREFILL step=0` plus `DECODE step=1`, allowing both old and replaced/grown buffers to be recognized during the profiled decode1 call; exclude future step=2/3 ranges;
- merge same-kind overlapping intervals for object-kind coverage;
- an overlap between WEIGHT and KV_CACHE object-kind ranges is a correctness STOP;
- a reference crossing a known-range boundary must not be silently counted as fully known.

Because the sidecar observations occur around the ROI rather than at every traced instruction, label the result as **runtime-range matching**, not exact per-instruction tensor lifetime attribution.

Never relabel UNKNOWN as activation/workspace without evidence.

## MP5 — Full formal coverage and page-footprint analysis

Run the corrected streaming analyzer on **all** formal traceg files for both prefill and decode1. Selectively extract compressed `traceg.xz` files if necessary; do not materialize full decompressed trace text.

Produce per ROI, and optionally per kernel if cheap:

- decoded memory-instruction count;
- decoded lane-reference count;
- requested bytes;
- WEIGHT reference count / requested bytes;
- KV_CACHE reference count / requested bytes;
- UNKNOWN reference count / requested bytes;
- cross-boundary/ambiguous count if any;
- unique 64KB pages touched by WEIGHT / KV_CACHE / UNKNOWN;
- unique 2MB pages touched by WEIGHT / KV_CACHE / UNKNOWN;
- min/max observed global-looking address where defensibly classifiable;
- decoder-format counts for list_all/base_stride/base_delta;
- decoder invariant failure count (must be zero).

For a memory reference of width >1, page-footprint accounting must include every page intersected by `[addr, addr+width)`, not only the starting page.

If conservative opcode grouping can be supported directly from recorded opcode names, optionally report GLOBAL/LOCAL/SHARED/OTHER subsets, but do not invent a memory-space classification. UNKNOWN object coverage is not synonymous with global non-Weight/KV traffic.

A full scan is expected to be streaming and bounded-memory. Lack of huge decompressed scratch is not by itself an acceptable reason to leave formal coverage UNKNOWN when the compressed `traceg.xz` data can be selectively staged and streamed.

STOP if the decoder cannot conservatively parse the formal trace format or if invariants fail.

## MP6 — Representative parser/simulator compatibility after semantic classification

Using the frozen parser compatibility anchor `73774727e25fadf89df6f30ef5cf014091115db7` and the existing SM86 parser configuration, perform bounded compatibility checks over semantic classes for both ROIs.

At minimum:

- ordinary COMPUTE: early/middle/late representative kernels and distinct-name samples;
- NCCL: at least one representative per observed NCCL semantic family, if present;
- any UNKNOWN_OTHER entry: inspect explicitly;
- compute-only list startup smoke.

Record whether each sample:

- header/parses successfully;
- simulator starts/binds successfully under the bounded smoke;
- fails due to unsupported opcode/format/collective semantics.

This is compatibility evidence only, not performance simulation. A failing NCCL simulator sample does not invalidate the raw capture; it becomes evidence for the later FULL_RANK0 vs COMPUTE_ONLY_TP_PARTITION integration decision.

Do not make that permanent decision in this stage.

## MP7 — Documentation cleanup and integration manifest

Update B-owned non-handoff documentation so it reflects completed capture and corrected offline semantics.

At minimum review/update as needed:

- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md` — remove stale pre-rental/no-trace status while preserving Route-E fidelity labels;
- `docs/vm_tlb/llm/NCCL_KERNEL_POLICY.md` — state that formal semantic classification uses embedded trace headers, not filenames;
- `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/KERNEL_MANIFESTS.md`;
- `.../METADATA_VALIDATION.md`;
- `.../OPEN_ISSUES.md`;
- `.../PARSER_SIM_COMPAT.md`;
- `.../VALIDATION_SUMMARY.md`;
- expand `FORMAL_DECODE1.md` to evidence parity with `FORMAL_PREFILL.md` using only actual archive/log facts.

Do not rewrite historical capture SHAs. Preserve the distinction:

- capture executable SHA = `c79f4469...`;
- later audit/documentation descendants are not capture executables.

Create an integration manifest that freezes:

- both archive paths/hashes;
- capture source/model/environment identities;
- corrected semantic full/compute-only/NCCL-only derivative hashes;
- corrected address-coverage output hashes;
- known Weight/KV coverage method and limitations;
- parser compatibility summary;
- unresolved NCCL policy = `DEFER_TO_M4B_INTEGRATION`;
- future Track-A integration rule: Core comes from accepted final Track-A M1–M3, not from the old frozen parser Core.

Do **not** merge `hrl/vm-m1-m3-v0` in this stage.

## MP8 — Closeout

Create:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/`

At minimum include:

- `README.md`
- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `RAW_LOG_INDEX.tsv`
- `SEMANTIC_KERNEL_CLASSIFICATION.md`
- `ADDRESS_COVERAGE.md`
- `PARSER_COMPAT.md`
- `INTEGRATION_MANIFEST.md`

Maintain:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

and `GOAL_PROGRESS.md` if it exists.

Final status must be exactly one:

- `M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION`
- `M4A_MERGE_PREP_BLOCKED`

Commit/push only explicit paths to `hrl/llm-trace-prep-v0`, then STOP for ChatGPT review.

# Hard STOP conditions

STOP rather than silently repairing assumptions if any of the following occurs:

- formal archive/hash/internal-manifest integrity failure;
- raw/full capture evidence would need modification;
- semantic kernel-name extraction is ambiguous for ordinary kernel entries;
- trace-address decoder cannot satisfy active-mask/reference-count invariants;
- Weight and KV recorded ranges overlap by object kind unexpectedly;
- formal scan produces malformed-address evidence not explained by the frozen tracer format;
- a result would require recapture or GPU access;
- a result would require Core VM changes;
- a result would require choosing a new paper-specific architecture semantic.

# Explicitly forbidden

Do not:

- access/rent a GPU;
- recapture prefill/decode1;
- modify either formal archive;
- modify Track-A branch or Core;
- merge A and B;
- implement Segmentation;
- implement L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/UVM/migration/MCM;
- permanently keep/drop NCCL for the paper reproduction;
- present runtime-range matching as exact tensor-lifetime ground truth.
