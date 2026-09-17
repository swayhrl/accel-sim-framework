# V31 addendum — OLMoE asset already finalized on node164

This addendum supersedes V31 Stage 0/1/2 only where they discuss searching, downloading, staging, or finalizing the OLMoE model asset.

## Confirmed finalized asset

The user has completed download, verification, and canonical finalization of:

- model: `allenai/OLMoE-1B-7B-0125-Instruct`
- immutable revision: `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`
- canonical root:
  `/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e/`
- expected canonical receipt:
  `MODEL_ASSET_RECEIPT.json`

The staging `.partial` directory was atomically moved into the final canonical root during finalize and should no longer exist.

The canonical directory must not contain symlinks.

## Hard execution rule

V31 is now an **existing-asset read-only authorization Goal**.

Do NOT:

- run `hf download` or equivalent model redownload;
- create another OLMoE staging copy;
- recreate/re-finalize the canonical asset;
- copy the full model to 174 local disk;
- duplicate the model elsewhere on node164;
- alter any file under the canonical asset root;
- replace canonical files with symlinks;
- mechanically re-hash every multi-GB shard when an accepted hash-bound `MODEL_ASSET_RECEIPT.json` already closes the identity chain.

## Revised Stage 0 — read-only asset authority audit

Start directly from the exact canonical root above.

Audit read-only:

1. `MODEL_ASSET_RECEIPT.json` exists and is parseable.
2. Receipt model ID exactly matches `allenai/OLMoE-1B-7B-0125-Instruct`.
3. Receipt revision exactly matches `b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`.
4. Canonical path revision matches the receipt revision.
5. Receipt file set closes against the directory's exact relative file set, excluding only receipt/schema-defined bookkeeping if appropriate.
6. No canonical file is a symlink.
7. Config/tokenizer/index/support files are present as required by the receipt.
8. Perform bounded re-hash of small authority-critical files such as config, tokenizer config, tokenizer/index/chat-template files where practical.
9. Treat the receipt's per-file hashes as the hard identity authority for large checkpoint shards unless a concrete mismatch/receipt defect is discovered.
10. Aggregate directory byte totals are derived sanity metadata only.

If the receipt or exact file set reveals a real mismatch, fail closed as an asset-identity blocker. Do not repair/re-download in this Goal.

## Continue automatically

If the read-only asset audit passes, continue immediately with the original V31:

`Stage 3 exact architecture/runtime contract -> Stage 4 canonical S2 input authority -> Stage 5 MoE dataflow/target hierarchy -> Stage 6 three-lineage comparability contract -> Stage 7 one-shot node109 producer contract -> review pack -> Git closure`

Do not stop merely because the asset is already finalized.

## Review-pack wording

`ASSET_AUTHORITY.json` should state that:

- the model was pre-existing and user-finalized before V31 execution;
- V31 performed read-only independent authority verification;
- no download/finalize/mutation occurred in V31;
- canonical asset root and immutable revision are exactly the values above.

The preferred final decision remains:

`C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

provided asset authority, S2 input authority, runtime/capacity policy, MoE target plan, and node109 producer contract all close.