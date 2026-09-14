# C16 RTX4080 CODEX_NEXT_STAGE

## Status

AUTHORIZED after the exact frozen input/token binding package is available locally.

Execute from this coordination branch using a fresh execution branch/worktree. Do not modify ChatGPT-owned handoff files.

## Objective

Resume from reviewed R3 execution:

`hrl/c16-4080-u4-u9-r3@920ab69ca4e59c60fd091e58b8d672f0923283d2`

U4 is already PASS. Do not repeat model admission unless a focused integrity recheck is needed.

Primary work:

1. verify the externally supplied frozen S0/B1/T128/Decode4/TEXT input/token binding;
2. complete U5 native baseline;
3. complete U6 RTX4080-local kernel census;
4. complete U7 bounded Llama NCU capture;
5. complete U9 address-bearing NVBit canary;
6. STOP.

## Reviewed prerequisites

- U4: `U4_LOCAL_ASSET_EXACT_CLOSURE_PASS`.
- Formal model path: `/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.
- U4 receipt SHA256: `5b1aed870cd03d50a0da5f6721ab639d56ca0f3a1c3782a9fed9cf8e3dc84a3b`.
- U8.5: `U8_5_C16_CUSTOM_TOOL_CLOSURE_PASS` from reviewed R1 evidence.
- NCU N0/N1: PASS.
- U0-U3 userspace runtime: PASS.

## Frozen U5 semantic identity

Required semantic contract:

`S0 / B1 / T128 / Decode4 / TEXT`

Do not reconstruct it from a prompt or tokenizer.

Do not re-tokenize.

Do not substitute a semantically equivalent prompt.

Do not infer token IDs from historical hashes.

The exact source-side package must bind the historical frozen input/token payloads and derived token IDs.

Reviewed R3 evidence names four required SHA256 identities:

- `bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208`
- `0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd`
- `f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7`
- `fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624`

## Stage A — admit frozen input/token binding

When the CPU/source server package arrives, first perform a live userspace-only admission:

1. inventory every supplied file;
2. record source provenance/receipt path;
3. recompute every payload SHA256;
4. bind the exact four historical hashes to their actual filenames/semantic roles;
5. verify exact S0/B1/T128/Decode4/TEXT identity;
6. verify derived token IDs are supplied as authoritative payload, not regenerated;
7. reject missing/extra/unbound payloads;
8. write a hash-closed RTX4080-side admission receipt.

If any required historical identity cannot be bound to actual bytes, STOP fail-closed.

## Stage B — U5 native Llama baseline

Begin only after Stage A PASS.

Use:

- exact formal model path from U4;
- exact frozen input/token binding from Stage A;
- Recovery-V2-S5 S0/B1/T128/Decode4/TEXT semantics;
- exact dtype and attention backend from the historical authority;
- CUDA-only residency;
- no offload/substitution;
- deterministic/frozen output checksum policy from the authority.

No NCU or NVBit in U5.

Record native wall time only as a platform reference. Do not treat timing as cross-platform-equivalent performance evidence.

## Stage C — U6 RTX4080-local kernel census

Begin only after U5 PASS.

Build a new census from the actual RTX4080 runtime/code objects.

Freeze target authority before U7/U9.

Never reuse RTX3090 launch IDs, ordinals, static instruction indices/ranges or `DYNAMIC_KERNEL_RANGE` as RTX4080 authority.

## Stage D — U7 bounded Llama NCU capture

Use only the qualified NCU 2025.1.1 executable.

Select a compact memory-characterization metric set from metrics actually supported on RTX4080; do not use `--set full`.

Freeze before capture:

- metric manifest/hash;
- U6-bound target/window;
- exact argv;
- exact model/input/runtime identity;
- timeout and cleanup policy.

Run NCU alone, never co-load NVBit. Store `.ncu-rep` under `/data/c16/ncu`, reopen/export with the same NCU, hash-close report/export/argv/target identity, and keep raw report out of Git.

## Stage E — U9 Llama NVBit address-bearing canary

Prerequisites:

- Stage A input binding PASS;
- U5 PASS;
- U6 target authority frozen;
- reviewed U8.5 lifecycle PASS remains bound to the exact custom tool closure used by U9.

Required sequence:

1. map actual RTX4080 live function/code object;
2. build SASS/static memory-instruction map;
3. no-match prewarm with READY proof;
4. immutable arm/target binding;
5. one bounded target capture;
6. clean process-group cleanup.

PASS requires:

- exact target launch observed;
- address-bearing rows > 0;
- complete schema/final newline;
- expected function/static binding;
- checksum-stable output;
- clean exit;
- raw trace size/SHA closure.

Do not broaden or reselect targets after freeze merely to obtain nonzero records.

## Concurrent bulk asset transfer policy

The CPU server may copy other model assets to RTX4080 while this Goal is waiting for the U5 input package.

Before U5/U7/U9 timing/profiling/capture begins, ensure any large background rsync into `/data/c16` is complete or paused and record a clean process/storage-I/O state. Do not run formal model measurements concurrently with bulk model migration.

## Allowed scope

Userspace work as `huangrulin` under the repo and `/data/c16`, including input/model validation, CUDA/NCU/NVBit work, bounded GPU experiments, receipts/manifests/hashes, ordinary user-owned downloads/copies, commit/push.

## Forbidden scope

Do not:

- use sudo or privilege escalation;
- mutate driver, host CUDA, kernel, modprobe, systemd, Docker daemon, network/proxy/DNS, mounts or storage layout;
- substitute model/revision/dtype/context/batch/backend/input/token binding;
- use CPU offload;
- re-tokenize to recreate the frozen token IDs;
- reuse RTX3090 target identities as RTX4080 authority;
- co-load NCU and NVBit in one formal run;
- commit weights, `.ncu-rep`, raw NVBit traces, wheel payloads, frozen input payloads, or large build artifacts.

## Required handoff output

Update:

`docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`

Create/update:

`docs/vm_tlb/review_packs/C16_4080_U5_U9_R4/`

Include at minimum `README.md`, `MANIFEST.json`, `SOURCE_ANCHORS.md`, `COMMIT_HISTORY.md`, `CHANGED_FILES.md`, `VALIDATION_SUMMARY.md`, `OPEN_ISSUES.md`, and `SHA256SUMS`.

`LATEST_REPORT.md` must state final branch/commit; input-binding/U5/U6/U7/U8.5/U9 status; blockers; important raw artifact paths+SHA; and `READY_FOR_NEXT_STAGE` or `NOT_READY`.

## Git requirements

- Fresh branch/worktree from this coordination branch.
- Do not rewrite ChatGPT-owned handoff files.
- Explicit-path staging; no `git add .` / `git add -A`.
- Raw artifacts stay out of Git.
- Run focused tests, `git diff --check`, clean-status and remote-head verification before report.

## STOP conditions

STOP when:

1. the exact frozen input/token package is absent or cannot bind the four historical SHA identities;
2. a genuine host/root mutation becomes unavoidable;
3. scientific identity cannot be closed without substitution/re-tokenization;
4. U9 completes.

Do not proceed to multi-model formal characterization in this stage.
