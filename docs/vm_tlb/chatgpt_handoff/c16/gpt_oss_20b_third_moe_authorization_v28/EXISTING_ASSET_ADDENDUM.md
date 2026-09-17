# V28 existing gpt-oss-20b asset addendum

This addendum is mandatory and must be read before the main V28 handoff.

## Asset status is already provisioned

`openai/gpt-oss-20b` has already been downloaded, finalized, and placed in the durable node164 C16 model-asset store.

Expected existing canonical root:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/gpt-oss-20b/6cee5e81ee83917806bbde320786a8fb61efebee`

Expected revision:

`6cee5e81ee83917806bbde320786a8fb61efebee`

Previous asset-ingest work produced a model-asset receipt and completed the finalization/acceptance step. V28 must verify the existing receipt/inventory and local files; it is **not** an asset-download or asset-provisioning Goal.

## Hard efficiency rules

Do NOT:

- run `hf download` / `huggingface-cli download` for gpt-oss-20b;
- redownload any model shard from the network;
- copy the full model to 174-new local disk;
- create another duplicate copy under node164;
- regenerate/re-finalize the already accepted model asset merely because V28 is creating a new review pack;
- transfer the full model to node109 during this CPU-only Goal;
- treat absence of a duplicate local copy as a blocker.

Use the existing node164 canonical asset in place, read-only.

## Stage-0 meaning

Stage 0 is an **authority reconciliation/audit**, not provisioning.

First locate and inspect the existing asset receipt if present under the canonical asset root or its established receipt/provenance location. Then verify enough of the existing local inventory to bind:

- model ID;
- revision;
- canonical root;
- exact file/subset identities required by the chosen executable runtime;
- config/tokenizer hashes;
- checkpoint/index hashes or receipt bindings;
- deterministic inventory/receipt identity.

Do not mechanically rehash tens of gigabytes if a previously accepted hash-bound receipt already provides strong file identity and only a bounded verification is needed. Rehash large shards only when the existing receipt is absent, internally inconsistent, or insufficient to bind the runtime-selected file subset.

Apply C16 evidence hierarchy:

- accepted hash-bound file/receipt identity is strong authority;
- aggregate directory size and descriptive total bytes are sanity metadata;
- do not fail solely on weak derived byte totals when the exact receipt/file identity closes.

## Multiple representations

The existing asset may contain more than one checkpoint/runtime representation. V28 must determine which exact subset the native gpt-oss runtime will actually load and distinguish:

- repository/canonical-asset total payload;
- native executable checkpoint subset;
- any alternate/original-format representation;
- tokenizer/config/runtime support files.

Do not require every stored representation to be copied or loaded for node109 execution.

## V28's actual deliverable

The purpose of 174-new V28 is:

`existing asset authority -> exact gpt-oss architecture/MXFP4 contract -> node109 runtime/capacity contract -> canonical S2 Harmony/token authority -> natural-routing MoE dataflow -> semantic target plan -> three-lineage comparability contract -> executable node109 producer contract`

No GPU execution and no model download belong in V28.
