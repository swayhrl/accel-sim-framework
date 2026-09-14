# C16 RTX4080 CODEX_NEXT_STAGE

## Status

AUTHORIZED.

Execute from this coordination branch using a fresh execution branch/worktree. Do not modify ChatGPT-owned handoff files.

## Objective

Resume from reviewed execution `c14dae683e7b3be580f484f9a585dc5e061c47d0`.

Do not repeat U0-U3, NCU N0/N1, or the already-closed U8.1-U8.7 diagnostics unless a direct regression requires a focused recheck.

Primary work:

1. reconcile and close U4 exact local Llama asset;
2. complete U5 native baseline;
3. complete U6 RTX4080-local kernel census;
4. complete U7 bounded Llama NCU capture;
5. complete U9 address-bearing NVBit canary;
6. STOP.

## Reviewed source anchors

- Latest Codex execution: `hrl/c16-4080-u4-u9-r1@c14dae683e7b3be580f484f9a585dc5e061c47d0`.
- Prior coordination handoff: `f1d088f21012b2d111c50ebd468418f17ee3b0ac`.
- U8.5 status at reviewed execution: `U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS`.
- Required model: `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.

Before execution read:

- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- `docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`
- `docs/vm_tlb/review_packs/C16_4080_U4_U9_R1/README.md`
- `C16_4080_MIGRATION_SOURCE_RECEIPT.md/json`

## Allowed scope

Userspace work as `huangrulin` under the repo and `/data/c16`, including model validation/promotion, CUDA/NCU/NVBit work, bounded GPU experiments, receipts/manifests/hashes, commit/push.

## Forbidden scope

Do not:

- use sudo or privilege escalation;
- mutate driver, host CUDA, kernel, modprobe, systemd, Docker daemon, network/proxy/DNS, mounts or storage layout;
- substitute model/revision/dtype/context/batch/backend;
- use CPU offload;
- reuse RTX3090 launch IDs/static ranges/targets as RTX4080 authority;
- co-load NCU and NVBit in one formal model process;
- commit model weights, `.ncu-rep`, raw NVBit traces, wheels, or large build artifacts.

If a genuine host mutation becomes unavoidable, exhaust userspace diagnosis, write a minimal administrator handoff with impact/rollback, and STOP.

## Stage A — reconcile U4 live asset state

Required incoming exact revision directory:

`/data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08`

There are two conflicting observations:

- operator post-rsync evidence showed six payload files present and source-vs-destination SHA256 equality;
- execution `c14dae68` observed the exact revision directory as empty.

The first action is a fresh live filesystem check. Record exact timestamp, directory inode/metadata if useful, file count, regular-file names, sizes and SHA256 values. Do not assume either prior observation is current truth.

If the directory is empty now:

- preserve the contradiction explicitly;
- do not redownload from Hugging Face;
- request/recover the exact transferred payload from the CPU server again;
- continue only after bytes are present and hash-closeable.

If files are present now, continue immediately.

## Stage B — authoritative source receipt

The CPU source server previously reported an `R1_LLAMA3P2_1B_ASSET_RECEIPT.json` or equivalent receipt that binds the exact model/revision and hash-closed payload identities.

The RTX4080 importer must continue requiring explicit `--source-receipt` provenance. Do not weaken this gate.

Search existing local/committed evidence first. If no exact source receipt exists locally, STOP only for the external action of copying that small receipt from the CPU server. Do not request Hugging Face authentication or a 2.4GB redownload.

Recommended destination for an externally supplied receipt is outside the payload directory, e.g.:

`/data/c16/models/.provenance/R1_LLAMA3P2_1B_ASSET_RECEIPT.json`

so the receipt itself is not accidentally counted as a model payload.

The importer may be adapted only to parse the actual receipt schema while preserving these invariants:

- exact model ID;
- exact revision;
- exact expected payload set;
- exact size for every payload;
- exact SHA256 for every payload;
- no directory-name-only provenance;
- no silent extra/missing files.

## Stage C — U4 validation and promotion

After live bytes and source receipt are both available:

1. inventory all regular payloads;
2. reject unexpected symlinks unless separately reviewed;
3. validate config/tokenizer/weight completeness/readability;
4. compare observed payload set, size and SHA256 exactly to source receipt;
5. bind exact model/revision from receipt;
6. emit `U4_LOCAL_ASSET_EXACT_CLOSURE_PASS` only on exact equality;
7. promote atomically to a stable exact-revision path under `/data/c16/models/`;
8. never overwrite an existing destination.

## Stage D — U5 native Llama baseline

Begin only after U4 PASS.

Freeze Recovery-V2-S5 semantic contract:

- S0 / B1 / T128 / Decode4 / TEXT;
- exact model revision;
- exact input/token receipt;
- dtype and attention backend;
- CUDA-only residency;
- no offload/substitution;
- output checksum;
- native wall-time as reference only.

No NCU or NVBit in U5.

## Stage E — U6 RTX4080-local kernel census

Begin only after U5 PASS.

Build a new census from the actual RTX4080 runtime/code objects. Freeze target authority before U7/U9 target-specific work.

Never reuse RTX3090 ordinals, launch IDs, static indices/ranges or `DYNAMIC_KERNEL_RANGE`.

## Stage F — U7 bounded Llama NCU capture

Use qualified NCU 2025.1.1 only.

Select a compact research-useful memory metric set from metrics actually supported on this RTX4080; do not use `--set full`.

Freeze before capture:

- metric manifest/hash;
- U6-bound target/window;
- exact argv;
- model/input/runtime identity;
- timeout/cleanup policy.

Run NCU alone. Store raw `.ncu-rep` under `/data/c16/ncu`, reopen/export with the same NCU, and hash-close report/export/argv/target identity. Raw artifacts stay out of Git.

## Stage G — U9 Llama NVBit address-bearing canary

Prerequisites:

- U4 PASS;
- U5 PASS;
- U6 target authority frozen;
- reviewed `U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS` remains valid for the exact tool closure used by U9.

Rebuild/map the actual RTX4080 live function and SASS/static memory target. Do not copy RTX3090 targets.

Required sequence:

1. live function/code-object mapping;
2. SASS/static memory-instruction map;
3. no-match prewarm with READY proof;
4. immutable arm/target binding;
5. one bounded target capture;
6. clean process-group cleanup.

PASS requires exact target launch observed, address-bearing rows > 0, complete schema/final newline, expected target binding, checksum-stable output, clean exit, and raw size/SHA closure.

Do not broaden or reselect targets after freeze merely to obtain nonzero records.

## Required handoff output

Update:

`docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`

Update/create review evidence under:

`docs/vm_tlb/review_packs/C16_4080_U4_U9_R2/`

At minimum include `README.md`, `MANIFEST.json`, `SOURCE_ANCHORS.md`, `COMMIT_HISTORY.md`, `CHANGED_FILES.md`, `VALIDATION_SUMMARY.md`, `OPEN_ISSUES.md`, and `SHA256SUMS`.

`LATEST_REPORT.md` must state final branch/commit; U4/U5/U6/U7/U8.5/U9 status; blockers; review-pack path; important raw artifact paths+SHA; and `READY_FOR_NEXT_STAGE` or `NOT_READY`.

## Git requirements

- Fresh branch/worktree from this coordination branch.
- Do not rewrite ChatGPT-owned handoff files.
- Explicit-path staging; no `git add .` / `git add -A`.
- Raw artifacts stay out of Git.
- Run focused tests, `git diff --check`, clean-status and remote-head verification before report.

## STOP conditions

STOP when:

1. the live incoming payload is absent and external re-transfer is required;
2. the authoritative small source receipt is absent and external copy is required;
3. a genuine host/root mutation becomes unavoidable;
4. scientific identity cannot be closed without substitution;
5. U9 completes.

Do not proceed to multi-model expansion in this stage.
