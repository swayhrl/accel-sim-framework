# CODEX 174-new Mainline V6-r1 — LDGSTS Consumer Analysis + Direct/Special Set-Level Integration

## 0. Execution mode and isolation

This is a **fresh-window, fresh-worktree, CPU-only scientific-analysis Goal** on node174-new.

Do not resume the previous 174-new Codex window. Do not reuse a dirty worktree.

Accepted 174-new analysis base:

`1447bf9bb19bd249c116f53287a1f768170848c7`

Producer authority to consume:

`hrl/c16-ldgsts-special-path-109-v5 @ ea43fa6331dcb2d7d6553f6a48000bdd004458e0`

Suggested implementation branch:

`hrl/c16-ldgsts-analysis-174new-v6-r1`

Suggested worktree:

`/root/workspace/accel-sim-framework-c16-ldgsts-analysis-174new-v6-r1`

Recommended bootstrap from the control repo:

```bash
cd /root/workspace/accel-sim-framework
git fetch origin --prune

git worktree add \
  /root/workspace/accel-sim-framework-c16-ldgsts-analysis-174new-v6-r1 \
  -b hrl/c16-ldgsts-analysis-174new-v6-r1 \
  1447bf9bb19bd249c116f53287a1f768170848c7
```

If the branch/worktree name already exists because of a failed attempt, do not attach to it blindly. Inspect and either remove the stale worktree safely or create an `-r2` name from the same accepted base. Never build on unreviewed local modifications.

No GPU workload. No CUDA inference. No producer rerun.

---

# 1. Scientific goal

Independently consume the V5 LDGSTS formal bundles now admitted on node164 and answer:

1. What memory behavior is visible in the newly captured **LDGSTS GLOBAL SOURCE** path?
2. How does it complement the previously accepted direct-GLOBAL-MREF evidence?
3. Does S2 Decode Early occurrence 24 differ from Late occurrence 767 once the actual global-to-shared read path is included?
4. How does S3 long-context Prefill Attention scale relative to S2 on the LDGSTS path?

Do **not** fabricate a single whole-kernel address stream from separate replay processes.

The strongest allowed combined coverage claim is:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

This means all detected address-bearing global paths are represented as independently closed sets. It does not imply temporal ordering across those sets.

---

# 2. Producer authorities and exact target bundles

Use Git review evidence only as an index; independently resolve each accepted run through node164 catalog/manifest.

Expected V5 producer targets:

| logical target | scenario/phase | occurrence | LDGSTS static count | expected executed/zero |
|---|---|---:|---:|---:|
| `Q05_S2_PREFILL_GEMM_LDGSTS` | S2_TEXT Prefill | 0 | 18 | 18 / 0 |
| `Q05_S2_PREFILL_ATTN_LDGSTS` | S2_TEXT Prefill | 0 | 48 | 48 / 0 |
| `Q05_S2_DECODE_EARLY_KV_LDGSTS` | S2_TEXT Decode | 24 | 84 | 33 / 51 |
| `Q05_S2_DECODE_LATE_KV_LDGSTS` | S2_TEXT Decode | 767 | 84 | 33 / 51 |
| `Q05_S3_PREFILL_ATTN_LDGSTS` | S3_TEXT Prefill | 0 | 48 | 48 / 0 |

Expected Pipeline run IDs:

```text
C16R_qwen25-05b_s2-text_prefill_nvbit-ldgsts-shard_q05-s2-prefill-gemm-ldgsts_20260915T093229Z_00d7e1404abc
C16R_qwen25-05b_s2-text_prefill_nvbit-ldgsts-shard_q05-s2-prefill-attn-ldgsts_20260915T093229Z_7ea3898f9bef
C16R_qwen25-05b_s2-text_decode_nvbit-ldgsts-shard_q05-s2-decode-early-kv-ldgsts_20260915T093229Z_f43f42b2e7e0
C16R_qwen25-05b_s2-text_decode_nvbit-ldgsts-shard_q05-s2-decode-late-kv-ldgsts_20260915T093229Z_c41730c29523
C16R_qwen25-05b_s3-text_prefill_nvbit-ldgsts-shard_q05-s3-prefill-attn-ldgsts_20260915T093229Z_9f20d86e164c
```

Do not hard-code the raw directory as scientific authority. The expected current accepted paths use:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/<RUN_ID>`

but the **catalog entry + RUN_MANIFEST.json** are authoritative. If catalog and expected path disagree, fail closed and report the discrepancy.

V5 producer review pack:

`docs/vm_tlb/review_packs/C16_LDGSTS_SPECIAL_PATH_109_V5/`

Important producer facts to independently verify:

- accepted operand index: `1`;
- accepted operand role: `GLOBAL_SOURCE`;
- operand `0` is shared destination;
- trace scope is same-process address context only;
- all accepted bundles are Pipeline ACKed;
- overflow/drop = 0;
- Decode zero-record shards are frozen as `ZERO_EXECUTION_PROVEN`.

---

# 3. Phase A — independent admission/raw closure

For each of the five V5 runs, perform an independent consumer-side closure before scientific parsing.

Required checks:

1. Locate exact immutable catalog entry for RUN_ID.
2. Locate raw bundle from catalog entry.
3. Reject symlinks where Pipeline V1 forbids them.
4. Validate exact file set against `RUN_MANIFEST.json`/`SHA256SUMS`.
5. Rehash every declared artifact independently.
6. Validate model/scenario/phase/target identity.
7. Validate static-set SHA and static-count against producer frozen-set evidence.
8. Validate each shard terminal record/status.
9. Validate `overflow == 0`, `drop == 0`.
10. Validate executed-vs-zero partition and exact counts.
11. Validate every replay's `C16_ADDRESS_CONTEXT_V1` sidecar hash and same-process binding.
12. Validate operand-selection metadata is bound to `operand_index=1`, `GLOBAL_SOURCE`.

Do not trust producer TSV totals as a substitute for raw closure.

Output:

`RUN_VERIFICATION.tsv`

with one row per formal run and explicit PASS/FAIL columns for all major closure checks.

Also output:

`OPERAND_BINDING_AUDIT.tsv`

that records the accepted SASS example and why operand 1 is the global source. The decision basis must be exact SASS/NVBit operand ordering, not address magnitude heuristics.

---

# 4. Phase B — decode LDGSTS special-path binary semantics

First inspect the raw bundle's binary/header schema and producer implementation before assuming the decoder format. If it is C16WARP1-compatible, reuse the qualified decoder path. If the producer extended the schema, implement a dedicated decoder with tests.

For every static LDGSTS shard:

- preserve static index;
- preserve function occurrence;
- classify `EXECUTED_SHARD` or `ZERO_EXECUTION_PROVEN`;
- for executed shards, decode active masks and lane addresses;
- count **active lane address events**, not merely producer callback count;
- compute start-address unique VA;
- start-address 4K, 64K, 2M page buckets;
- start-address 128B line buckets.

### Width semantics

LDGSTS opcode/SASS such as:

`LDGSTS.E.BYPASS.LTC128B.128`

may be treated as exact 16-byte access width only if the hash-bound exact static SASS/opcode validation proves that width. Do not infer width from a generic name parser if it could be ambiguous.

When width is exact, also compute exact touched:

- 4K pages;
- 64K pages;
- 2M pages;
- 128B lines.

When width is not exact, retain:

`WIDTH_UNKNOWN`

and use only start-address buckets.

### Access-kind semantics

For the selected operand 1 GLOBAL SOURCE of LDGSTS, semantic global access kind is `READ`, provided the exact qualified instruction semantics are bound. Record the classification source.

Output detailed per-static-row data in:

`SPECIAL_PATH_FINGERPRINT.tsv`

Recommended columns:

```text
target run_id static_index occurrence classification opcode sass access_kind width_classification width_bytes active_lane_events start_unique_va start_4k_pages start_64k_pages start_2m_pages start_128b_lines exact_touched_4k_pages exact_touched_64k_pages exact_touched_2m_pages exact_touched_128b_lines static_set_sha trace_sha address_context_sha
```

---

# 5. Phase C — same-process semantic object attribution

For each executed shard, use **only that replay's own same-process ADDRESS_CONTEXT ranges**.

Never apply an object map/range table generated by a different CUDA process.

Allowed classes include:

- `WEIGHT`
- `KV_CACHE`
- `ACTIVATION`
- `UNKNOWN_RUNTIME`

If the producer sidecar carries more precise validated subclasses, preserve them, but do not invent semantic labels.

For each address event:

1. identify zero/one/multiple matching ranges;
2. zero match -> `UNKNOWN_RUNTIME`;
3. one valid matching range -> classify to exact recorded class/name;
4. overlapping ambiguous matches -> fail closed to `AMBIGUOUS_RUNTIME_RANGE` or equivalent, not a guessed class.

Output:

`OBJECT_ATTRIBUTION.tsv`

with at least per-target/per-static counts and bytes when width exact.

If the current same-process object ranges still fail to cover active addresses, that is a valid result; do not weaken the run.

---

# 6. Phase D — integrate with accepted direct-GLOBAL-MREF evidence

Use accepted consumer outputs from prior 174-new analysis. Do not rewrite the old review packs.

Primary accepted analysis base:

`docs/vm_tlb/review_packs/C16_QWEN0_DECODE_ANALYSIS_174NEW_V4/`

Also use accepted Prefill direct-path analysis/hardening evidence already present in the repo and bound to its exact producer hashes.

For each matching target, create a set-level coverage row containing:

- direct static count;
- direct executed/zero count;
- direct active-lane address events;
- LDGSTS static count;
- LDGSTS executed/zero count;
- LDGSTS active-lane address events;
- direct access kinds;
- LDGSTS access kind (`READ` if proven);
- per-path object composition;
- per-path width certainty;
- coverage qualification.

Do **not** compute:

- cross-path absolute-VA union;
- cross-path page/line union;
- direct+LDGSTS reuse distance;
- direct+LDGSTS temporal sequence.

Output:

`DIRECT_PLUS_LDGSTS_COVERAGE.tsv`

Coverage label may be promoted to:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

only where the V4 full-function audit + V5 qualified LDGSTS closure supports it.

Note: `LDGDEPBAR` is memory-control/dependency machinery, not an address-bearing global path. Keep it out of address-path counts.

---

# 7. Phase E — highest-priority Decode Early vs Late analysis

Compare:

- Early occurrence: 24
- Late occurrence: 767
- exact same Flash function/static-set family

The producer quickcheck reports the same executed/zero partition (33/51), while producer callback totals differ. Consumer analysis must recompute the true decoded metrics and must not equate callback count with lane-address-event count.

Required comparisons:

1. exact static-set identity;
2. exact executed static-index set relation;
3. per-static active-lane-event delta;
4. total active-lane-event delta;
5. start-page/line counts per executed shard;
6. exact touched page/line counts where width is exact;
7. object-class composition;
8. matched same semantic object identity only if independently provable;
9. object-relative offsets only for a common semantic object identity with lossless range binding.

Forbidden:

- absolute-VA direct comparison across replay processes;
- cross-shard union pretending to be a whole-kernel footprint;
- interpreting event-count delta as KV growth unless semantic/object evidence supports that interpretation.

Output:

`DECODE_EARLY_LATE_SPECIAL_COMPARISON.tsv`

Also produce a short `DECODE_EARLY_LATE_FINDINGS.md` that clearly separates:

- observed facts;
- supported interpretation;
- unsupported hypotheses.

---

# 8. Phase F — S2 vs S3 Prefill Attention scaling

S2 context is T2048; S3 context is T8192. The known Flash grid changed from `16x1x14` to `64x1x14`.

Compare the **same special-path family** across S2 and S3 using count-normalized evidence.

Required metrics:

- static-set identity/count;
- executed static-index set;
- decoded active-lane address events;
- per-static event scaling;
- page/line footprints per shard;
- width-exact touched metrics;
- object composition when same-process ranges match.

Useful normalization examples:

- S3/S2 event ratio;
- event count per context token;
- page count per context token;
- line count per context token.

Do not claim global temporal reuse or physical whole-kernel footprint.

### S3 direct path

If S3 direct formal run has not yet been independently consumed by 174-new, also ingest the V4 S3 direct run as a scoped prerequisite:

`C16R_qwen25-05b_s3-text_prefill_nvbit-warp-mref-shard_s3-attention_20260915T081217Z_9796e9f72cfc`

Use its catalog/manifests as authority. Do not silently treat producer TSV as consumer-accepted data.

Output:

`S2_S3_SPECIAL_COMPARISON.tsv`

and, if S3 direct ingestion was needed, include it explicitly in `RUN_VERIFICATION.tsv` with evidence class identified as the direct path rather than LDGSTS.

---

# 9. Regression, immutability, and resource rules

Must remain true:

- CPU-only;
- no GPU/model workload;
- no retokenization;
- no raw mutation;
- no modification of accepted old review packs;
- no catalog-path rewrite;
- no directory move/delete/rename on node164 formal data;
- no cross-process absolute-VA joins.

Rerun the exact RTX3090 Q2 regression suite after shared parser changes.

Preserve previously accepted Qwen0 direct-path regression checks.

Use streaming/chunked parsing. Do not materialize huge decoded traces in `/tmp` or RAM.

---

# 10. Tests

Add CPU tests for at least:

1. LDGSTS operand qualification metadata binding;
2. zero-record shard -> `ZERO_EXECUTION_PROVEN` only when terminal closure proves it;
3. nonzero overflow/drop -> fail closed;
4. exact `.128` width parsing/validation;
5. start-bucket vs exact-touched distinction;
6. same-process object-range match;
7. cross-process range join prohibited;
8. no absolute-VA union across shards;
9. direct+LDGSTS integration emits coverage inventory but no fabricated union;
10. Decode early/late comparison deterministic;
11. S2/S3 normalization deterministic;
12. Q2 exact regression unchanged.

---

# 11. Review pack

Create:

`docs/vm_tlb/review_packs/C16_LDGSTS_ANALYSIS_174NEW_V6_R1/`

Include at minimum:

- `README.md`
- `FINAL_DECISION.json`
- `RUN_VERIFICATION.tsv`
- `OPERAND_BINDING_AUDIT.tsv`
- `SPECIAL_PATH_FINGERPRINT.tsv`
- `OBJECT_ATTRIBUTION.tsv`
- `DIRECT_PLUS_LDGSTS_COVERAGE.tsv`
- `DECODE_EARLY_LATE_SPECIAL_COMPARISON.tsv`
- `DECODE_EARLY_LATE_FINDINGS.md`
- `S2_S3_SPECIAL_COMPARISON.tsv`
- `REGRESSION_RESULTS.tsv`
- `DERIVED_RECEIPT.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

`DERIVED_RECEIPT.json` must be self-contained and list each derived output's relative path, size and SHA256. Timestamps may be separate from deterministic payload hashes.

Expected success label:

`C16_LDGSTS_ANALYSIS_174NEW_V6_R1_PASS`

Scoped pass is acceptable if object attribution remains unknown, provided raw/static/address-context closure is complete and scientific claims are correspondingly narrow.

Any mismatch in raw hashes, operand authority, static-set identity, terminal closure or overflow/drop is blocking and must fail closed.

Commit/push the implementation branch, report branch + HEAD + decision + key scientific observations, then STOP.
