# Qwen3-30B-A3B reproducible redownload runbook

Status: `UNVERIFIED_LOCAL_SHARDS_DISCARDED_BY_AUTHORIZED_SPACE_RECOVERY`.

## Immutable source contract

| Field | Value |
| --- | --- |
| Model | `Qwen/Qwen3-30B-A3B` |
| Fixed model/tokenizer revision | `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` |
| Checkpoint set | 16 safetensors, `61,066,575,648` bytes total |
| Frozen per-file expected size and LFS SHA-256 | `MODEL_ASSET_MANIFEST.tsv`, SHA-256 `e5b6cdaa0049296259e24ed330dc4d1cb56f149763fa12895cac5724e693413f` |
| Model root on this host | `/workspace/c16_assets/c16-a/metadata/Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` |

The source manifest is authoritative for every shard name, exact expected byte
count, and frozen remote LFS SHA-256.  A remote LFS declaration is not a local
asset receipt.

## Proven transport and required closure

The following transport worked for shards 1--10 before the intentional space
recovery discard:

```text
curl --http1.1 --continue-at - --fail --location --connect-timeout 15 \
  --retry 8 --retry-all-errors --limit-rate 1M \
  --output <model-root>/<shard>.incomplete \
  https://huggingface.co/Qwen/Qwen3-30B-A3B/resolve/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/<shard>
```

For each shard, retain the same partial path and use range continuation after a
recoverable interruption.  Do not accept `.incomplete` as a checkpoint.  The
required per-shard state machine is:

```text
fixed revision URL -> complete byte count -> expected-size match
-> exactly one whole-file SHA-256 against frozen LFS SHA-256
-> immutable verified receipt -> accepted local asset
```

The pre-discard downloader successfully produced ten final-sized files, but
did not write any immutable receipts.  They were therefore never accepted
assets, were never included in P0--P3, and must not be treated as SHA-verified
after re-download.  Future automation must emit the receipt immediately after
the one permitted whole-file SHA pass and must make heartbeat discovery follow
the active shard rather than only shard 1.

## Resource and concurrency guardrails

- Start a new 30B worker only when real filesystem available bytes are at
  least 85 GiB; use one low-priority 1 MiB/s worker initially.
- Pause the 30B worker, without deletion, below 15 GiB available space.
- Wave-1 P2/P3 are already immutable and must never be modified or used for
  space recovery. Qwen3-30B-A3B is Wave-2 only: `NOT_FOR_RTX3090`, not P0--P3,
  and no CPU offload/GPU/profiler/NVBit/simulator action is authorized.
- Consider raising 30B concurrency only after a measured aggregate-throughput
  comparison; retain the lower level if throughput does not improve.

## Authorized discard receipt

At the time of deletion, shards `model-00001-of-00016.safetensors` through
`model-00010-of-00016.safetensors` were complete-sized but had zero immutable
receipt closures. Their combined unverified bytes were `39,993,966,728`.
They are the only checkpoint files authorized for removal by this recovery
operation. Model metadata/tokenizer files, the frozen manifest, P0--P3,
Wave-1 assets, and operational logs remain outside the deletion scope.

Deletion completed after no 30B curl/downloader process remained. The ten
explicit files were absent on post-delete inspection; `39,993,966,728` bytes
were released. Filesystem available bytes increased from `9,813,942,272`
before deletion to `49,807,106,048` afterward. This removal is recoverable
only by the pinned-revision re-download and closure sequence above.
