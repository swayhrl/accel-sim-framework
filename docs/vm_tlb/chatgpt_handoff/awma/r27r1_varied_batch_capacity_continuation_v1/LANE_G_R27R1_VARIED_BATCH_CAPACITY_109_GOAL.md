# Codex Goal — Lane G / node109
## AWMA R27R1 varied-batch capacity continuation V1

Date: 2026-10-03 (Asia/Shanghai)

Repository: `swayhrl/accel-sim-framework`

Stage: `AWMA_R27R1_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch: `hrl/awma-r27r1-varied-batch-capacity-continuation-handoff-v1`

Execution branch: `hrl/awma-r27r1-varied-batch-capacity-109-v1`

Closed R27 execution: `4dca1cd713df8315b9e04f702d7f3b990c8f4b88`, tree `03debf7395f51062c133ad4d534791f2b5fc1770`.

This is a **new reviewed continuation**, not a resume of the closed R27 execution branch. Start from the exact published handoff HEAD/tree in the launch instruction, create a fresh worktree/branch, and preserve the R27 STOP record unchanged.

The scientific question is unchanged: does the accepted R26 one-physical-batch C1/S2 capacity distinction survive a fixed genuinely varied text stream, and if positive does the S2-only witness survive 32 continuous steps and fresh-process recovery?

This Goal is one bounded solve-and-continue chain. Passing gates continue automatically. A scientific/identity/source/numerical/resource STOP closes this execution. Do not ask for approval between passing gates.

## 0. Mandatory read order

Read completely:

1. `START_HERE.md`
2. `ACCEPTED_R27_REVIEW.md`
3. `SOURCE_AUTHORITY.json`
4. this Goal
5. `R27R1_EXPERIMENT_CONTRACT.json`
6. repository `AGENTS.md`

The task-specific Goal/contract supersede older R27 operational text only for this new execution. Historical R26/R27 evidence and STOP labels remain immutable.

## 1. Gate A — accepted-parent identity recheck, CPU/read-only

Do **not** rerun the full R27 207-item historical Gate-A audit by default.

Instead:

- verify the closed R27 execution commit/tree and its review-pack identity;
- read its `R26_RAW_READBACK.json`, `FINAL_DECISION.json`, `SHA256SUMS` and accepted review snapshot;
- verify the exact R26 common checkpoint to be consumed is still the 2,626,691,315-byte CPU snapshot with SHA256 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`, logical step 1;
- verify the frozen R26 source/model identities against the accepted R27 authority before using them.

If any consumed authority is missing, mismatched or contradicts the accepted R27 review, classify `R27R1_PARENT_AUTHORITY_NOT_QUALIFIED` and STOP. If identities match, reuse the accepted `R27_PARENT_RAW_QUALIFIED` conclusion; do not spend another round re-reading all 207 historical payloads.

This reuse is evidence reuse, not relabeling: R27 remains the run that performed the full raw readback.

## 2. Gate B0 — exact input acquisition and durable admission, CPU-only

The sole scientific payload is defined in `SOURCE_AUTHORITY.json`:

- Salesforce `wikitext`
- scientific revision `8aaa8b27d493dba10b8553290236799e6dc57829`
- config `wikitext-2-raw-v1`
- train split
- file `wikitext-2-raw-v1/train-00000-of-00001.parquet`
- exact bytes: 6,357,543
- exact SHA256: `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`

Acquisition is transport, not scientific selection. Accepted ways to obtain the bytes:

1. the original pinned official Salesforce/Hugging Face resolve URL;
2. the official Salesforce/wikitext current-main resolve URL;
3. a user-provided or already-local cached file.

Options 2–3 are admissible **only after the local file is exactly 6,357,543 bytes and has the exact SHA256 above**. Do not accept text equivalence, reserialized parquet, another mirror with unverified bytes, another split or another corpus.

Bound all network attempts. Do not loop indefinitely. If the exact payload cannot be acquired, record attempts and STOP as `R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED`. This is still not a GPU negative.

Once acquired:

- copy the exact raw bytes without transformation into a durable node164 input-authority directory under the existing C16/AWMA namespace;
- create an immutable admission receipt binding source metadata, acquisition route, local path, node164 path, bytes and SHA256;
- read back node164 size/SHA and require an exact match;
- retain the producer copy until node164 admission ACK is complete;
- do not tokenize before the raw payload itself is admitted.

Gate B0 is CPU/network/storage only. No CUDA/JIT and no GPU lock acquisition.

## 3. Gate B1 — frozen varied bank, scoped implementation and numerical qualification

Use only the already accepted local Llama tokenizer identity from R26/R27. Do not download or replace model/tokenizer assets.

Read the parquet `text` column in physical row order. Join **all** row strings with one LF between rows, including empty rows. Tokenize once with `add_special_tokens=False`. Record parquet SHA, text SHA, tokenizer class/version and exact tokenizer-file SHA.

Require at least 540,672 token IDs. Take exactly the first 540,672 IDs and reshape C row-major to CPU int64 `[33,128,128]`. Require all 4,224 128-token windows to be byte-distinct. If insufficient or duplicate, STOP as `R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED`; do not shift offset or choose another slice.

Freeze and publish:

- full bank SHA;
- every step/row/window binding;
- exact source/tokenizer identities;
- step semantics.

For step `k=0..32` and tested B:

- input: `bank[k,0:B,0:127]`
- labels: `bank[k,0:B,1:128]`
- attention: all ones
- loss: mean over B×127 labels.

Use step 32 only for next-loss checks.

### Scoped code

Create new R27R1 code under `util/vm_tlb/awma/r27r1_varied_batch_capacity/`. Keep R26 and closed R27 source unchanged.

Reuse the accepted R26 tied-W component semantics:

- same Llama revision and six-payload model identity;
- BF16 tied input-embedding/lm-head W only trainable;
- full frozen backbone forward and dH backward;
- FP32 AdamW m/v unchanged;
- C1 remains default;
- S2 is explicit capacity opt-in;
- C1 retains one full V×H total gradient;
- S2 uses 4096-row tiles and no full V×H gradient/shadow;
- no dynamic policy, no automatic OOM retry/fallback;
- no offload, activation checkpointing, allocator tuning, precision/attention/tile/optimizer sweep;
- no `empty_cache`/GC between training steps.

Use the exact R26 common CPU state without another bootstrap. A narrow migration may bind only the new bank identity/cursor. It must not change W/m/v/logical step/RNG.

### B1 pre-freeze numerical gate

From the same migrated start, run the first four bank steps at B1 for B0/C1/S2. Fixed `rtol=atol=1e-2`. Check every step:

- loss;
- dH;
- total gradient;
- W;
- m;
- v;
- exact logical step/cursor;
- next-bank forward loss;
- finite state.

Also check fresh-process checkpoint load and one C1↔S2 policy switch on the new stream without moment/cursor/counter reset.

Ordinary engineering defects may be fixed and affected pre-freeze gates rerun. A true numerical/identity failure is `R27R1_NUMERIC_OR_STATE_NOT_QUALIFIED` and STOP.

Only after Gate A + B0 + B1 pass, write `IMPLEMENTATION_FREEZE.json`. The freeze must precede every capacity observation. After freeze, any required change to GPU behavior, data, classifier, tolerance, tile, optimizer or input binding is STOP/review rather than an implicit retry.

## 4. Gate C — bounded natural capacity boundary

Use the frozen implementation and bank only.

Each trial:

- fresh process;
- same CPU start;
- five actual continuous training steps using bank indices 0..4;
- two designated warmups plus three further complete steps;
- finite loss/W/m/v;
- exact counters;
- no state restore between steps;
- no graph/state leak;
- record whole-step and phase allocated/reserved, post-step active state, failed request and traceback on OOM.

Search separately C1 then S2:

- start B64;
- after PASS: B96, then B128 until OOM or right-censored PASS;
- after B64 OOM: B32,16,8,4,2,1 until first PASS;
- refine by integer floor midpoint until adjacent PASS/OOM;
- at most 12 distinct search B per policy.

Classify only unambiguous CUDA OOM as OOM. Timeout, crash, CPU kill, numeric failure, device fault or conflicting job is UNKNOWN and STOP/qualification failure, never OOM.

Confirm each adjacent endpoint in 3 fresh processes, no majority vote and no extra repetition to manufacture stability. If B128 PASS, mark right-censored and do not extrapolate.

Define `B_common=min(C1_max_PASS,S2_max_PASS)`.

A positive forward witness requires C1 confirmed OOM at `C1_max_PASS+1` and S2 confirmed PASS at that same B. If there is no stable forward witness, publish the actual equal/regressed/censored/negative result and STOP without Gate D.

No formal timing campaign is authorized. Per-step latency/memory may be retained as feasibility descriptors only.

## 5. Gate D — positive-only 32-step trajectory and recovery

Only after a stable C1-OOM/S2-PASS same-B witness:

1. At B_common, compare one C1/S2 step from the identical state on bank step 0: loss, dH, total gradient and updated W/m/v.
2. Run C1 and S2 for 32 consecutive steps using bank indices 0..31 from identical starts. Compare loss and next-loss each step; full W/m/v at trajectory indices 1/4/8/16/32; exact logical step/cursor each step.
3. Fresh-process resume each policy from its step-16 CPU checkpoint for the remaining 16 steps and compare final state/loss.
4. From the same C1 step-16 checkpoint, run the next step under C1 and S2 to verify policy switch without reset.
5. Independently run S2 at B_witness for 32 continuous varying-input steps with finite state, input hashes and memory/liveness checks. Fresh-process resume from its step-16 checkpoint.

Do not invent a matched C1 numerical reference at the witness B when C1 OOMs there.

If five-step witness passes but 32-step, state recovery or liveness fails, classify `R27R1_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED`. Preserve the five-step observation separately; do not lower B, change allocator settings or retune S2 to rescue the stronger claim.

If all gates pass, classify `R27R1_VARIED_BATCH_CAPACITY_EXTENSION_32_STEP_SUPPORTED` with the exact model/source/bank/tied-W/hardware/software scope.

## 6. GPU/resource control

Every CUDA/JIT operation, including B1 numerical qualification, must hold a real `flock` on:

`/data/c16/locks/c16_gpu_campaign.lock`

for the full parent/subprocess lifetime.

Before the first GPU operation, verify no competing campaign process. One GPU campaign at a time. No artificial VRAM pressure.

Input acquisition/admission remains CPU-only and must not acquire the GPU lock.

## 7. Publication and STOP

Node164 is durable authority for:

- exact raw parquet;
- bank authority;
- checkpoints;
- raw trials/logs;
- manifests/receipts.

Git contains compact code and one review pack:

`docs/vm_tlb/review_packs/AWMA_R27R1_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1/`

Include:

- accepted-parent recheck receipt;
- input acquisition and node164 admission receipt;
- source/bank/tokenizer identities;
- `IMPLEMENTATION_FREEZE.json`;
- numerical qualification;
- every capacity trial;
- endpoint confirmations;
- Gate-D trajectory/resume evidence if reached;
- `RAW_DATA_INDEX.tsv`;
- `SHA256SUMS`;
- resource-lock/process closure;
- generic CPU finalizer and final decision.

Final report:

`docs/vm_tlb/codex_handoff/awma/r27r1_varied_batch_capacity_continuation_v1/LANE_G_FINAL_REPORT.md`

Publish exact execution commit, push, fetch back, verify remote SHA/tree, clean worktree, node164 readback, no campaign CUDA process and released lock. Then STOP.

Do not automatically start production integration, another input/model, formal timing, profiler, node174/Accel-Sim, hardware/PPA or deployment. ChatGPT reviews the result before any next stage.
