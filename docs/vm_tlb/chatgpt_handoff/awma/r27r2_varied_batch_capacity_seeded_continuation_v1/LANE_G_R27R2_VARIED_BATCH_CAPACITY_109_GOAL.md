# Codex Goal — Lane G / node109
## AWMA R27R2 seeded varied-batch capacity stability V1

Date: 2026-10-03 (Asia/Shanghai)

Repository: `swayhrl/accel-sim-framework`

Stage:
`AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch:
`hrl/awma-r27r2-varied-batch-capacity-seeded-continuation-handoff-v1`

Fresh execution branch:
`hrl/awma-r27r2-varied-batch-capacity-109-v1`

Closed R27R1:
`254d66f69ec81bf932add705f721f36255feef2c`,
tree `ebefec69e9ba153adfaf5d1f7860a956964d09cb`.

This is one **merged solve-and-continue Goal**. The user explicitly requested fewer rounds and higher execution efficiency. Do not split external-seed admission, token-bank construction, B1 numerical qualification, implementation freeze, capacity search, positive-only 32-step/resume, or bounded positive-only diagnostics into separate Codex rounds. Passing gates continue immediately in this execution. Only a real scientific/identity/numerical/resource STOP returns to ChatGPT.

R27 and R27R1 remain immutable historical STOPs. Do not resume, amend, rewrite, or delete them.

## 0. Scientific question

R26 accepted one narrow repeated-sequence tied-W capacity distinction:
C1 B70 PASS / B71 OOM versus S2 B71 PASS / B72 OOM, each 3/3 under a five-step complete training loop. R27/R27R1 never reached varied-input observation because the exact new parquet bytes were unavailable.

R27R2 asks the originally intended falsifiable question:

> Does the same C1/S2 capacity distinction survive a fixed genuinely varied train-text stream, and if a stable same-B C1-OOM/S2-PASS witness exists, does the S2 witness survive 32 continuous steps and fresh-process recovery?

No convergence, quality, throughput, all-parameter training, deployment, hardware or general-memory claim follows automatically.

## 1. Read order / authority

Read completely:

1. `START_HERE.md`
2. `ACCEPTED_R27R1_REVIEW.md`
3. `SOURCE_SEED_AUTHORITY.json`
4. this Goal
5. `R27R2_EXPERIMENT_CONTRACT.json`
6. repository `AGENTS.md`

Start from the exact published handoff HEAD/tree in the launch instruction and create an isolated execution worktree. The execution branch is based on the handoff, not directly on R26/R27/R27R1.

Use accepted R27/R27R1 evidence rather than repeating historical audits. The sole new premise is that an external byte-exact source seed has now been staged for R27R2.

## 2. Gate A — bounded parent check + exact external seed admission

### A1. Parent authority recheck

Do not rerun the historical 207-item R27 raw audit.

Bounded checks only:

- exact closed R27R1 commit/tree and accepted review-pack identity;
- accepted `R27R1_PARENT_AUTHORITY_QUALIFIED` status;
- R26 common CPU checkpoint:
  - 2,626,691,315 bytes;
  - SHA256 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`;
  - logical step 1;
  - accepted W/m/v/RNG/model identity;
- frozen R26 component/runner/capacity-search source and CCE source consumed by this run;
- accepted local Llama model/tokenizer payload identities.

If any consumed authority is missing/mismatched, STOP:
`R27R2_PARENT_OR_SEED_NOT_QUALIFIED`.

### A2. External seed validation — no network retries

Preferred path:

`/data/c16/awma/r27_input_seed/train-00000-of-00001.parquet`

If absent, perform at most one bounded local scan under:

`/data/c16/awma/r27_input_seed`

for regular files of exactly 6,357,543 bytes; hash each candidate. Do **not** perform any network URL download attempt in this Goal.

The only admissible payload is exact:

- file identity: Salesforce/wikitext, revision `8aaa8b27d493dba10b8553290236799e6dc57829`;
- config `wikitext-2-raw-v1`;
- train split;
- 6,357,543 bytes;
- SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`.

Reject any other bytes regardless of equivalent text/content.

Once exact:

1. create a producer-side seed receipt containing staging path, bytes, SHA, mtime only as metadata, and scientific source identity;
2. copy the raw bytes **without transformation** to a stage-specific node164 immutable input-authority path under the existing AWMA/C16 namespace;
3. use safe partial/staging semantics appropriate to the existing node164 data plane;
4. independently read back node164 size and SHA;
5. only after exact readback PASS emit `R27R2_EXACT_INPUT_ADMITTED`;
6. preserve the staging copy until durable admission ACK is complete.

No tokenization before exact node164 admission. Gate A is CPU/storage only: CUDA/JIT=0 and GPU lock acquisitions=0.

If the staged seed is absent or hash/size fails, STOP. Do not revert to network retry.

## 3. Gate B — token bank + numerical qualification + implementation freeze

After exact input admission, continue immediately.

### B1. Frozen bank construction

Use only the accepted local Llama tokenizer already qualified in R26/R27/R27R1. No model/tokenizer download or replacement.

Read the parquet `text` column in physical row order. Join every row string with one LF between rows, preserving empty strings. Tokenize the resulting text exactly once with:

`add_special_tokens=False`.

Record:

- raw parquet bytes/SHA;
- row count;
- joined-text SHA;
- tokenizer class/version;
- tokenizer payload SHA;
- token count;
- exact flags.

Require at least 540,672 token IDs.

Take exactly the **first** 540,672 IDs. No search for a convenient offset. Reshape C row-major to CPU int64:

`[33,128,128]`.

This defines 4,224 windows of 128 tokens. Require all 4,224 windows to be byte-distinct. If insufficient tokens or any duplicate window exists, STOP as `R27R2_PARENT_OR_SEED_NOT_QUALIFIED`; do not change the slice or source.

Persist the immutable bank and a compact bank manifest on node164; read back hash/size before GPU use.

For k=0..32 and batch B:

- input = `bank[k,0:B,0:127]`;
- labels = `bank[k,0:B,1:128]`;
- attention = ones;
- loss = mean over B×127 labels.

Step k=32 is reserved for next-loss checks.

### B2. R27R2 scoped implementation

Create new code only under:

`util/vm_tlb/awma/r27r2_varied_batch_capacity/`.

Do not modify R26/R27/R27R1 historical source.

Reuse accepted R26 scientific semantics:

- same Llama model/revision/payloads;
- BF16 tied input embedding/lm-head W only trainable;
- exact tied storage/pointer relationship;
- full frozen backbone forward and dH backward;
- unchanged explicit FP32 AdamW m/v and optimizer constants;
- C1 default;
- S2 explicit capacity opt-in;
- C1 retains its full V×H total gradient;
- S2 uses 4096-row tiles and no full V×H gradient/shadow;
- no OOM fallback;
- no offload/checkpointing;
- no precision/attention/tile/optimizer tuning;
- no per-step `empty_cache`/GC.

Reuse exact R26 common CPU state; do not bootstrap again. A narrow migration may bind only the new input-bank identity/cursor. W/m/v/logical step/RNG must remain unchanged.

### B3. B1 numerical pre-freeze gate

From identical migrated starts, run B0/C1/S2 on B1 for bank steps 0..3.

Fixed:
`rtol=atol=1e-2`.

At each step compare:

- loss;
- dH;
- total gradient;
- W;
- m;
- v;
- logical step;
- stream cursor;
- next-bank forward loss;
- finite state.

Also require:

- fresh-process checkpoint load/resume;
- one policy switch from a common checkpoint without reset of moments/cursor/counter.

Use chunked CPU comparison where needed; avoid unnecessary giant duplicated state.

A true identity/numerical/state mismatch STOPs:
`R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED`.

Ordinary engineering defects may be repaired **inside this Goal before freeze**, then rerun only the affected pre-freeze gate and its dependencies. Do not create a separate repair round.

### B4. Freeze

Only after A + bank authority + B1 numerical/state qualification all PASS, create:

`IMPLEMENTATION_FREEZE.json`.

Freeze all scientific inputs/behavior before any capacity observation:

- source/bank/tokenizer hashes;
- R26 common start identity;
- model/optimizer/tile;
- component source and CCE source;
- runtime/backend versions;
- per-step input semantics;
- capacity search algorithm;
- PASS/OOM/UNKNOWN classifier;
- numerical tolerance;
- lock/resource contract.

After freeze, a change to input, GPU behavior, classifier, tolerance, tile, optimizer or capacity semantics requires STOP/review. Pure report/path fixes that cannot change observations may be corrected.

## 4. Gate C — natural capacity search and endpoint closure

Continue automatically after freeze.

Each capacity trial:

- fresh process;
- same frozen CPU start;
- one policy and one B;
- bank steps 0..4;
- five actual continuous complete training steps;
- first two designated warmups, followed by three further complete steps;
- no checkpoint restore between steps;
- finite loss/W/m/v;
- exact logical step/cursor and input hash each step;
- graph/state liveness;
- post-step active allocation;
- whole-step/phase allocated/reserved;
- exact failed request/traceback if OOM.

Search policy order: C1 then S2.

For each policy:

1. B64.
2. If PASS: B96, then B128 until OOM or B128 PASS.
3. If B64 OOM: B32,16,8,4,2,1 until first PASS.
4. Once L PASS / U OOM exist, repeatedly test floor((L+U)/2) until U=L+1.
5. At most 12 distinct search B per policy.

B128 PASS is right-censored; never extrapolate.

Only unambiguous CUDA OOM is OOM. Timeout, generic crash, CPU kill, device fault, numeric failure, resource conflict or unknown failure is UNKNOWN and cannot be reclassified.

Require monotonicity. Any contradictory/nonmonotone/UNKNOWN boundary closes as `R27R2_CAPACITY_BOUNDARY_UNSTABLE`.

### Endpoint confirmation

Confirm each largest PASS and adjacent OOM in **three fresh processes each**. No majority vote, no extra repetitions to manufacture a stable result.

When endpoints overlap across policies, reuse exact matching confirmations where scientifically identical; otherwise run only missing confirmations. Alternate policy order where useful to avoid systematic ordering bias, while maintaining one GPU campaign process at a time.

Set:

`B_common = min(C1_max_confirmed_PASS, S2_max_confirmed_PASS)`.

A forward positive witness is:

- C1 confirmed OOM 3/3 at `B_witness=C1_max_PASS+1`;
- S2 confirmed PASS 3/3 at exactly the same B.

If no forward witness:

- equal endpoints → `R27R2_NO_VARIED_BATCH_CAPACITY_EXTENSION`;
- S2 worse → `R27R2_S2_BATCH_CAPACITY_REGRESSION`;
- censored case → `R27R2_CAPACITY_RIGHT_CENSORED`;
- unstable → corresponding unstable STOP.

Publish and STOP without Gate D.

No formal timing campaign. Trial latency/memory may be descriptive only.

## 5. Gate D — positive-only 32-step / resume / switch

Only after stable forward same-B witness.

### D1. Common-B one-step numerical

At B_common, from identical frozen starts, compare one C1/S2 step on bank step 0:

- loss;
- dH;
- total gradient;
- updated W/m/v;
- logical step/cursor;
- next-loss.

Same fixed tolerance.

### D2. Common-B 32-step trajectories

Run C1 and S2 independently for bank steps 0..31 from identical starts.

Every step compare/report:

- loss;
- next-bank loss;
- logical step;
- stream cursor;
- finite state;
- memory/liveness.

Full W/m/v checks at trajectory indices:
1, 4, 8, 16, 32.

Do not retain all giant states unnecessarily; keep only the required step-16/final checkpoints and chunk comparisons.

After trajectory index 16, logical step must be 17; after index 32, logical step must be 33.

### D3. Fresh-process recovery

For each policy, resume from its step-16 CPU checkpoint in a fresh process and execute the remaining 16 steps. Final state/loss/cursor must match the uninterrupted trajectory.

### D4. Policy switch

From the same C1 step-16 state, run the next bank step once under C1 and once under S2, preserving state/moments/cursor semantics.

### D5. Witness-B S2 32-step

At the forward witness B, run S2 for 32 continuous varied-input steps and fresh-process resume from index 16. Require finite state, exact input hashes/cursors and stable resource/liveness behavior.

Do not invent a matched C1 numerical trajectory at B_witness because C1 OOM is the witness condition.

If five-step capacity witness passes but any D requirement fails, preserve the five-step result and classify:
`R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED`.

Do not shrink B, change allocator configuration, or retune S2 to rescue the stronger result.

If all D gates pass:
`R27R2_VARIED_BATCH_CAPACITY_EXTENSION_32_STEP_SUPPORTED`,
strictly scoped to this exact model, start, fixed varied train stream, tied-W-only training, RTX4080/software environment and frozen implementation.

## 6. Optional Gate E — only if positive and attribution remains genuinely unresolved

Do not automatically run allocator diagnostics.

Only if Gate D fully passes **and** existing trial receipts cannot explain the allocation/liveness distinction sufficiently for interpretation, allow at most one fresh C1/S2 diagnostic pair at B_witness using bounded PyTorch allocator history/snapshot or `memory_stats`.

This diagnostic:

- is not an endpoint confirmation;
- is not a timing sample;
- cannot change allocator/backend;
- cannot justify additional exploratory GPU sweeps;
- must document PyTorch visibility limits.

Skip Gate E if unnecessary.

## 7. GPU / concurrency / efficiency rules

Before first CUDA/JIT:

- verify the exact seed/bank authority has PASSed;
- inspect GPU process/VRAM state;
- acquire a real `flock` on `/data/c16/locks/c16_gpu_campaign.lock`.

Every CUDA/JIT parent/subprocess remains under the lock for its full lifetime.

This Goal is logically sequential across scientific gates, but within a gate:

- CPU hash/parsing/finalization work with no mutable-state conflict may run concurrently;
- independent CPU comparisons may be parallelized after resource inspection;
- never run competing GPU campaign processes;
- never mutate the same manifest/checkpoint/result file concurrently.

Reuse already-qualified immutable identities and results where the contract permits. Do not redo expensive work merely to create a fresh receipt.

## 8. Publication / final closure

Node164 durable authority contains:

- exact admitted raw parquet;
- immutable token bank + manifest;
- checkpoints;
- all raw capacity/trajectory/diagnostic outputs;
- manifests/receipts/logs.

Git contains compact code plus one review pack:

`docs/vm_tlb/review_packs/AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/`.

Include at minimum:

- parent/seed admission receipt;
- node164 seed/bank readback;
- source/tokenizer/bank identities;
- numerical qualification;
- `IMPLEMENTATION_FREEZE.json`;
- generic search/finalizer code;
- all search trials and endpoint confirmations;
- capacity decision;
- D trajectory/resume/switch evidence if reached;
- E diagnostic only if reached;
- first mismatch/failure evidence;
- `RAW_DATA_INDEX.tsv`;
- `SHA256SUMS`;
- GPU lock/process/resource closure;
- final decision.

Final report:

`docs/vm_tlb/codex_handoff/awma/r27r2_varied_batch_capacity_seeded_continuation_v1/LANE_G_FINAL_REPORT.md`.

Complete:

- node164 publication/readback;
- `git diff --check`;
- explicit staging;
- commit;
- push;
- fetch-back exact SHA/tree verification;
- clean execution worktree;
- no campaign CUDA processes;
- GPU lock released.

Then STOP.

Do not automatically start production hardening/default enable, formal timing, another corpus/model, node174/Accel-Sim, profiler, hardware/PPA, all-parameter training or deployment. ChatGPT reviews the complete merged result before any next stage.
