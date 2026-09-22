# C16 OLMoE V40 — Selector Authority Provenance Repair V1

## Why this repair exists

The historical V38 review pack froze:
- selected count = 243
- historical normalized selector SHA256 =
  `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

However, the exact normalized-selector serialization algorithm and the full 243-row V38 selector were not committed.

The V39/V39R2 handoffs explicitly acknowledge that V38 committed only the summary and required V39R2 to regenerate all 243 rows. V39R2 later reported that it reproduced the 1096/243 identities and both historical SHA values, but the regenerated 243-row artifact and the hash-generation algorithm were still not committed to Git.

Therefore the historical `9d2d...` value is an accepted historical summary checksum but is **not independently reproducible from the durable authority materials now available**.

Do not guess an algorithm and do not brute-force canonicalizations until one happens to collide.

## Scientific interpretation

This is a provenance/reproducibility defect in a historical summary checksum, not evidence that the actual-A target or the V40 captured 243-static membership changed.

V40 actually used the persisted complete 243-row selector under:
`/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv`

and captured one independently validated shard for every selected static.

The repair must not:
- change the model/input/semantic target;
- change actual-JIT variant-A conditioning;
- add/remove selected statics merely to recover the old checksum;
- relabel failed/incomplete attempts as zero;
- claim that `9d2d...` was independently recomputed if it was not.

## One bounded recovery search

Before declaring the historical algorithm unrecoverable, perform one bounded provenance search on node109 for a retained exact producer or command.

Search only likely durable/local evidence locations, for example:
- `/data/c16/olmoe_v38*`
- `/data/c16/olmoe_v39*`
- `/data/c16/olmoe_v39r2*`
- relevant C16 worktrees/review packs/scripts
- exact-hash textual references to `9d2d414999e417200167664dc0b4c716f1dcfb72aaf505d89736e14dbedbcb33`

The search is for an exact script/command/artifact that itself defines the serialization.

Do not spend another long round trying arbitrary TSV/JSON formatting permutations.

If an exact historical producer is found:
- freeze and hash it;
- reproduce `9d2d...`;
- record the algorithm and artifact in the final review pack;
- no provenance repair is needed beyond documenting it.

If no exact producer is found after the bounded search, continue with the repair below.

## New durable selector authority

Freeze the exact complete selector that V40 actually consumed.

Source:
`/data/c16/olmoe_v39r2/VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv`

Required structural checks before freezing:
1. exactly 243 data rows;
2. exactly 243 unique `static_index` values;
3. every index is in the accepted actual-A 1096-static domain;
4. membership exactly equals the 243 statics represented by the V40 formal shard set;
5. no FAILED_EXCLUDED shard;
6. known typed anchors 101, 103, 1085 are members;
7. the raw TSV is immutable for the authority bundle.

Record its exact literal byte SHA256 as:
`selector_raw_tsv_sha256`.

## Canonical serialization: C16_SELECTOR_CANONICAL_V1

Define a new reproducible canonical selector hash. This is a **new authority hash**, not a reinterpretation of the historical V38 `9d2d...`.

Algorithm:

1. Parse the TSV using UTF-8 text and tab delimiters.
2. Reject duplicate column names.
3. Reject rows with missing or extra fields.
4. Require a `static_index` column.
5. Treat every parsed field value as its exact TSV string value; do not numerically reformat PC/opcode/register/width strings.
6. Reject duplicate `static_index` values.
7. Sort rows by numeric `int(static_index, 0)` ascending.
8. Sort the column-name list lexicographically by Unicode code point.
9. For each sorted row, construct an object containing exactly the sorted column names mapped to their exact string values.
10. Construct the top-level object exactly as:
    `{"schema":"C16_SELECTOR_CANONICAL_V1","columns":[...],"rows":[...]}`
11. Serialize with Python:
    `json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"`
12. Encode as UTF-8.
13. SHA256 the resulting bytes.

Persist:
- the canonical UTF-8 bytes as `VARIANT_A_COMPLETE_STATIC_SELECTOR.canonical_v1.json`;
- its SHA256 as `selector_canonical_v1_sha256`;
- the exact canonicalizer source used to generate it;
- the raw TSV literal SHA;
- row/column counts.

The canonicalizer itself must be committed to Git and hashed in the review pack.

## Required authority receipt

Create a receipt such as:
`SELECTOR_AUTHORITY_REPAIR_V1.json`

with at least:

- `status = PASS_PROVENANCE_REPAIR`
- historical V38 normalized SHA = `9d2d...`
- historical hash status = `OPAQUE_HISTORICAL_CHECKSUM_SERIALIZATION_NOT_DURABLY_RETAINED`
- V39R2 historical report status = `REPORTED_REPRODUCED_BUT_PRODUCER_NOT_DURABLY_RETAINED`
- source raw TSV path
- raw TSV SHA256
- canonicalization schema = `C16_SELECTOR_CANONICAL_V1`
- canonicalizer source path/SHA256
- canonical selector SHA256
- row count = 243
- unique static count = 243
- exact formal-shard membership equality = true
- typed anchors present = [101, 103, 1085]
- scientific identity changed = false
- GPU recapture required = false

## Hardening rule after this repair

The V40 formalizer/admission path must fail closed on the new durable authority:

- raw TSV SHA must match the frozen `selector_raw_tsv_sha256`;
- canonical V1 SHA must match the frozen `selector_canonical_v1_sha256`;
- 243 static membership must equal the V40 formal shard membership;
- tool/replay/function SHA sets must each be exactly one non-null value;
- all 243 validators/lifecycle gates must still pass.

The historical `9d2d...` must remain visible in provenance, but must **not** be used as a machine-recomputed admission gate unless its exact historical producer is actually recovered.

## Claim boundary

Allowed:
- V38 historically recorded selector count 243 and normalized SHA `9d2d...`.
- V39R2 historically reported reproducing that identity.
- the exact historical serialization was not durably retained.
- V40 repaired provenance by freezing the complete selector actually consumed by the formal campaign with a new explicit canonical scheme.

Not allowed:
- “V40 independently reproduced `9d2d...`” unless the exact producer is recovered and the hash is actually reproduced.
- silently replacing the meaning of `9d2d...` with the new canonical V1 hash.

## Execution impact

This repair is CPU-only.

Do not recapture the 243 GPU shards if:
- the existing selector has 243 unique members;
- it exactly matches the 243 formal shard membership;
- every shard remains independently valid;
- all other frozen scientific identity gates remain closed.

After the repair and CPU re-audit PASS, continue:
final producer review pack
→ Pipeline V1 finalize
→ publish to `hrl174new` inbox `.partial`
→ STOP for independent 174-new authority admission.
