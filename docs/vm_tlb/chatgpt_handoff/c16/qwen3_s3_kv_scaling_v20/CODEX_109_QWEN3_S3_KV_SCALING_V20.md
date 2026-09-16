# C16 Qwen3 S3 KV context-scaling campaign — node109 V20

## Execution mode

Execute this task in **GOAL MODE**. This is one autonomous producer Goal. Do not stop after setup, state capture, replay preparation, static audit, or partial formal capture while downstream stages remain executable.

The scientific objective is to compare the **same semantic target** across Qwen3 S2 and S3:

`layer0.self_attn.repeat_kv(K)`

Evidence class remains strictly:

`KV_STORAGE_DIRECT_READ`

Do not relabel QK/AV as direct KV-cache reads. QK/AV remain `KV_DERIVED_ATTENTION_CORE_READ` only when backed by the established typed dataflow.

## Immutable authorities

Model:

- `Qwen/Qwen3-8B`
- revision `b968826d9c46dd6066d109eabc6255188de91218`
- BF16
- eager attention

S2 accepted producer authority:

- producer HEAD `5d29ad8babe47226cbd25180a6db133e9526b6cf`
- run `C16R_qwen3-8b_s2-text_decode_nvbit-warp-mref-shard_v18r2-k-repeat_20260916T040000Z_ee18ee18ee18`
- target `layer0.self_attn.repeat_kv(K)`
- V18R2 source manifest SHA256 `3a189ae86864e723a7fc0b8fd739db8c3fe3befa33800ee2c444e799f0ad75b8`
- V18R2 catalog SHA256 `a043d78b0069f1acd24d5fdc2fc75ccac32b1e1aa3fa1da55a137e26f24b19ad`

S2 independent consumer authority:

- V19 HEAD `925ab0507abb50ebbe4b177d98d9bf3809d1bcd7`
- independently recomputed 160 static MREF, 8 executed, 152 zero, 2048 active-lane events for the accepted V18R2 raw

V19R1 scope-audit branch:

`hrl/c16-qwen3-kv-scope-audit-174new-v19r1`

Canonical repository:

`https://github.com/swayhrl/accel-sim-framework.git`

The 174-new transport was independently closed using existing GitHub CLI + HTTPS credentials with the hard condition:

`LOCAL == git ls-remote SHA == authenticated gh api SHA`

Do not alter authentication mechanisms merely to run this Goal.

S3 canonical V2 input:

- scenario `S3_TEXT`
- B1 / T8192 / D16
- payload SHA256 `4acf772ccf5596edb0a2589624b5fd0e61da447024ca23bf944118dc948c36c2`
- validated by the same V2 canonical-input authority used for Qwen3 S2

No model/revision/precision/backend/input substitution is permitted.

## Stage 0 — import the literal V19R1 scope result

Before any GPU work, fetch/read the exact V19R1 review pack from the canonical repository. Use bounded retrieval only:

1. normal Git fetch of the exact implementation ref;
2. if command stdout is unreliable, redirect to files;
3. if needed, use authenticated `gh api` against `repos/swayhrl/accel-sim-framework`.

Do not search for alternative Qwen3 runs.

Read the literal scope classification from the V19R1 review pack (`KV_SCOPE_AUDIT.json`, `FINAL_DECISION.json`, `NEXT_STEP_AUTHORIZATION.json`, or the exact equivalent artifact produced by V19R1).

Record the literal value in the V20 review pack.

Allowed branches:

### A. `FULL_SCOPE_VALIDATED`

Use the accepted V18R2 S2 run as the full-scope S2 baseline. Do **not** re-admit a duplicate S2 run.

Proceed directly to S3.

### B. `SCOPED_CAPTURE_ONLY`

The V18R2 semantic/object proof remains useful, but its dynamic event totals are slice-local. Before S3, repair S2 capture scope in this same V20 Goal using the exact same semantic target and a minimal isolated replay described below. Admit the corrected S2 run, wait for positive ACK, then continue automatically to S3.

### C. `WRONG_OCCURRENCE` or `BLOCKED_INSUFFICIENT_EVIDENCE`

Treat the accepted V18R2 formal dynamic scope as unsuitable for context scaling. Perform the same bounded isolated S2 recapture correction below. Do not mutate/delete the old accepted run; preserve it as typed historical evidence. After corrected S2 ACK, continue to S3.

Do not stop after Stage 0 unless the literal V19R1 result truly cannot be recovered after the bounded Git/gh methods above.

## Stage 1 — establish a capture method that is unambiguously full-scope

For every new formal capture in V20, avoid the V18R2 ambiguity by using a **minimal dedicated K-post replay process**.

### 1.1 Exact K-post state

For S2 repair when required, recover the exact qualified S2 first-decode K-post tensor from the accepted exact state/replay chain.

For S3, generate the exact first-decode state from the canonical S3 payload using the already-authorized exact semantic layer-streaming method:

checkpoint -> selective exact loader -> all 36 true decoder layers -> true KV cache -> true next token -> layer0 first decode -> exact post-update K

No synthetic hidden states, lower precision, alternate backend, or fake KV may be used.

Expected semantic shapes:

- S2 post-update K: `[1,8,2049,128]`
- S3 post-update K: `[1,8,8193,128]`
- repeat output expands KV heads 8 -> 32

Persist exact state hashes and tensor shape/dtype/stride/storage metadata.

### 1.2 Isolated replay

Create a fresh process whose scientific operation is only:

1. load the exact frozen CPU K-post tensor;
2. transfer it to CUDA;
3. call pinned Transformers 4.51.0 `repeat_kv(K, num_key_value_groups)` exactly once under the target NVTX range;
4. synchronize and emit output/hash metadata.

Avoid executing another instance of the same CUDA direct-copy function before the target call.

The isolated replay must prove:

- source is the exact K-post tensor for that scenario;
- repeat output is bitwise equal to the corresponding in-context/instrumented repeat output;
- source/destination are non-aliasing;
- kernel function/grid/block signature matches the in-context semantic target for the same scenario.

### 1.3 Clean capture environment

Before every formal shard subprocess explicitly remove any inherited scope filters, including at least:

- `C16_CTA_BEGIN`
- `C16_CTA_END`

and any equivalent inherited CTA/block range selector.

Set the required function/static selector explicitly. Do not rely on a shell's inherited C16 capture state.

Use a fresh per-run output root.

## Stage 2 — S3 semantic and signature qualification

Using S3 B1/T8192 first decode:

1. prove exact S3 input SHA and model/revision/runtime;
2. prove the true first-decode K-post state;
3. prove `repeat_kv(K)` dataflow:
   `KV_POST_UPDATE_K -> KV_DERIVED_REPEAT_K`;
4. preserve QK/AV only as reads of the proven derived repeat buffers;
5. establish in-context vs isolated-replay signature equivalence;
6. record S3 kernel grid/block and compare descriptively against S2.

Do not require the S3 grid to equal S2; context scaling is expected to change launch extent.

## Stage 3 — fresh static/global-address-path audit

For the actual S3 isolated repeat-K function:

- obtain fresh SM89 SASS/static map or prove exact binary/function identity and regenerate the target static set;
- audit direct GLOBAL MREF;
- independently audit LDGSTS / GLOBAL_TO_SHARED;
- audit other address-bearing special paths;
- do not count pure control/memory-control instructions as address-bearing accesses.

Freeze the complete static MREF set before formal capture.

If the function is binary-identical to S2, record that fact and compare static-set SHA, but do not silently assume identity.

## Stage 4 — complete formal capture

Capture every frozen static MREF shard for the exact isolated repeat-K replay.

Requirements:

- `FORMAL_ADMISSION_CONCURRENCY=1`;
- expected shard count == present shard count;
- every shard terminal closed;
- drop total == 0;
- overflow total == 0;
- every shard has same-process `ADDRESS_CONTEXT`;
- executed vs `ZERO_EXECUTION_PROVEN` classification is explicit;
- exact semantic target identity is recorded.

Capacity must be large enough for full S3 launch coverage. Do not silently keep a capacity that truncates the larger S3 grid.

### Full-scope post-capture gate

Independently decode the new traces before admission.

For all executed shards record CTA coverage and object membership. At minimum require:

- no inherited CTA slicing evidence;
- union of CTA coordinates for the K-source-read dynamic evidence is consistent with the entire target grid, including expected lower/upper CTA extent;
- active source-read addresses losslessly join the same-process `KV_POST_UPDATE_K` range;
- no evidence that function occurrence selected a different launch.

If evidence shows only a CTA subset, STOP before admission with a typed blocker; do not call it full-scope.

## Stage 5 — Pipeline admission

If Stage 0 required corrected S2 recapture:

1. close corrected S2 formal bundle;
2. admit exactly one S2 run;
3. wait for positive receiver verification/catalog/ACK;
4. only then begin/admit S3.

Never have two formal admissions in flight.

For S3:

- transfer to node164;
- verify destination artifacts/hashes;
- perform serial admission;
- wait for positive ACK;
- preserve catalog entry path/SHA, source manifest SHA and verification SHA.

Do not modify/delete previous accepted raw/catalog entries.

## Stage 6 — NCU

Preserve a bounded NCU report for the exact S3 isolated replay.

Record metric values only when explicit values and units are available. Preserve native-unit uncertainty and the known cache-control warning if present. Do not infer bytes from ambiguous display units and do not use uncontrolled-cache NCU as a strong cross-scenario cache-effect claim.

## Stage 7 — S2 -> S3 context-scaling comparison

Only compare against a **full-scope S2 baseline**:

- accepted V18R2 if V19R1 says `FULL_SCOPE_VALIDATED`;
- otherwise the corrected S2 V20 run.

Use the same validated C16WARP1 methodology on both sides.

Compare at least:

- semantic target identity;
- K-post / repeat tensor shapes;
- kernel function/grid/block;
- static MREF set size and SHA;
- executed/zero partition;
- total active-lane events;
- per-executed-shard event distribution;
- per-shard 4K/64K/2M page distributions;
- per-shard 128B line distributions;
- same-process KV_POST_UPDATE_K membership;
- formal completeness/drop/overflow;
- typed NCU comparability.

Safe cross-scenario statements:

- event-count ratios for the same full-scope semantic/static target;
- per-shard footprint-count scaling;
- launch-dimension scaling.

Forbidden:

- cross-process absolute VA comparison;
- cross-replay VA union;
- invented cross-shard chronology;
- reuse distance reconstructed from independent shards;
- cache/TLB causality from event-count scaling alone.

## Stage 8 — review pack and decision

Create a hash-closed V20 review pack under:

`docs/vm_tlb/review_packs/C16_QWEN3_S3_KV_SCALING_109_V20/`

It must include at least:

- imported V19R1 scope decision;
- S2 baseline authority (accepted or corrected);
- S3 canonical input/state receipt;
- S3 dataflow/replay/signature evidence;
- fresh static/path audit;
- S3 formal shard/manifest summary;
- full-scope CTA/object-membership audit;
- Pipeline admission/ACK evidence;
- NCU typed evidence;
- S2-vs-S3 comparison;
- `FINAL_DECISION`;
- `OPEN_ISSUES`;
- `SHA256SUMS`.

A PASS must be scoped to the exact `repeat_kv(K)` KV-storage materialization path. Do not promote this single target to a claim about all Attention/KV behavior.

## Stage 9 — Git transport closure

Use the node's existing Git authentication mechanism; do not change it unless genuinely broken.

Suggested implementation branch:

`hrl/c16-qwen3-s3-kv-scaling-109-v20`

After all scientific artifacts are committed and the working tree is clean:

1. push actual `HEAD:refs/heads/hrl/c16-qwen3-s3-kv-scaling-109-v20`;
2. verify the canonical repository identity is `swayhrl/accel-sim-framework`;
3. verify final SHA through canonical `git ls-remote`;
4. when authenticated `gh api` is available, verify the same branch SHA through GitHub API;
5. success requires nonempty remote SHA and exact equality with final local HEAD.

Do not ask the user to perform routine Git closure manually.

## Stop conditions

Fail closed only for a real blocker such as:

- canonical input/model hash mismatch;
- exact S3 state cannot be produced without prohibited substitution;
- replay/signature mismatch;
- static/address-path closure failure;
- full-scope gate proves slicing/wrong occurrence that cannot be corrected by the bounded isolated method;
- drop/overflow;
- Pipeline rejection/negative verification;
- terminal artifact corruption.

On a blocker, preserve all valid evidence, hash-close a typed partial review pack, commit/push it, verify canonical remote HEAD, and STOP.

Otherwise continue automatically through the entire V20 Goal and STOP only after final remote verification.
