# CODEX 174-new Lane B Goal — C16 Prospective Common Input Authority V8

Accepted Lane B base: `cd74256d698d9949d222703db8bb077a3581792a`.

Suggested branch: `hrl/c16-prospective-common-input-174new-laneB-v8`.

CPU-only. No GPU/model execution. No network download. Do not rewrite historical Qwen2.5 bindings or the adopted Llama S0 authority.

## Objective

Remove the prospective-input blocker for future Llama/Qwen3-8B/DeepSeek cross-model work by creating a new, explicitly prospective, hash-closed common source family. This is not historical recovery.

Authority label:

`C16_PROSPECTIVE_COMMON_INPUT_V1`

Historical and prospective axes must remain separately queryable.

## P0 — New common source authority

Create deterministic, original, repository-controlled UTF-8 sources for:
- `TEXT`
- `CODE`
- `STRUCTURED`

Do not reverse-decode historical token IDs. Do not copy an external/copyrighted corpus. Prefer a small checked-in deterministic generator plus fixed seed/template data that can regenerate byte-identical sources.

Each generated source must be long enough that every targeted local tokenizer can produce at least 8192 tokens where required.

Freeze:
- generator source SHA;
- generator/version identity;
- source file SHA256 and byte count;
- normalization policy (no implicit Unicode/whitespace normalization beyond exactly documented generation);
- deterministic truncation policy.

Recommended token policy for this prospective family:
1. load exact local canonical tokenizer assets only;
2. `add_special_tokens=False` unless a model-specific mandatory behavior is explicitly proven and recorded;
3. encode the complete common source bytes/text deterministically;
4. take the first exact N token IDs for the scenario;
5. fail closed if fewer than N tokens are available;
6. S4 may deliberately replicate one exact 2048-token STRUCTURED sequence across batch=4, but record that policy explicitly.

Do not silently apply chat templates.

## P1 — Target models

Attempt prospective bindings for all six canonical C16 model assets so the future cross-model axis is common:
- Llama-3.2-1B `4e20de362430cd3b72f300e6b0f18e50e7166e08`
- Qwen2.5-0.5B-Instruct `7ae557604adf67be50417f59c2c2f167def9a775`
- Qwen2.5-7B-Instruct raw `a09a35458c702b33eeacc393d103063234e8bc28`
- Qwen2.5-7B-Instruct-AWQ `b25037543e9394b818fdfca67ab2a00ecc7dd641`
- Qwen3-8B `b968826d9c46dd6066d109eabc6255188de91218`
- DeepSeek-V2-Lite `604d5664dddd88a0433dbae533b7fe9472482de0`

Use only tokenizer assets already present in each canonical model archive. If a tokenizer requires model-provided local code, bind exact local code/config identity and keep network disabled.

## P2 — Scenario family

Create prospective bindings for the established shapes where source class applies:
- S0_TEXT B1/T128/D4
- S1_CODE B1/T256/D16
- S2_TEXT B1/T2048/D32
- S2_CODE B1/T2048/D32
- S2_STRUCTURED B1/T2048/D32
- S3_TEXT B1/T8192/D16
- S4_STRUCTURED B4/T2048/D16

For every model/scenario, record:
- prospective authority class;
- model id/revision;
- tokenizer file/config/code identities and SHA where practical;
- source class/path/SHA;
- generation/truncation policy SHA;
- token count;
- canonical token-sequence SHA under one documented serialization;
- payload file SHA if a payload is materialized;
- batch/context/decode parameters;
- no-retokenization-after-freeze rule.

Do not mark any row `HISTORICAL_FROZEN_BINDING` or `FORMAL_ACCEPTED`.

## P3 — Storage and immutability

Keep compact generator/policy/source manifests in Git. Store materialized token payloads/receipts under a clearly prospective node164 provenance/input namespace, not in historical recovery paths.

Use no-overwrite/fail-closed promotion for any node164 authority directory. Produce a receipt/index sufficient for future node109 staging without retokenization.

## P4 — Compatibility audit

For raw7B vs AWQ, verify whether prospective common-input token sequences are identical when exact tokenizer identities are equivalent; record the result but do not use this V1 authority to rewrite or replace the currently accepted AWQ formal S2 evidence.

For Qwen3-8B and DeepSeek, record tokenizer/runtime caveats needed by a future deployment.

## P5 — Keep Qwen3-30B out of scope

Qwen3-30B-A3B remains `ASSET_NOT_FOUND`. Do not download it and do not create a binding for an absent canonical asset.

## Tests

- generator produces byte-identical source files on repeat;
- tokenizer load is offline/local-only;
- each scenario has exact requested token count;
- canonical token-sequence hash deterministic;
- fail closed on insufficient source length;
- fail closed if tokenizer identity/revision cannot be bound;
- historical authority files are byte-identical before/after;
- repeated compact indexes are byte-identical.

## Review pack

Create `docs/vm_tlb/review_packs/C16_PROSPECTIVE_COMMON_INPUT_174NEW_LANEB_V8/` including at least:
- `FINAL_DECISION.json`
- `COMMON_SOURCE_AUTHORITY.json`
- `COMMON_SOURCE_INDEX.tsv`
- `PROSPECTIVE_BINDING_INDEX.tsv`
- `TOKENIZER_IDENTITY_INDEX.tsv`
- `RAW7B_AWQ_PROSPECTIVE_TOKEN_COMPATIBILITY.json`
- test results
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed success:
- `C16_PROSPECTIVE_COMMON_INPUT_174NEW_LANEB_V8_PASS`
- `..._PASS_WITH_GAPS` for model-specific tokenizer issues that are explicitly isolated.

Commit/push and STOP.
