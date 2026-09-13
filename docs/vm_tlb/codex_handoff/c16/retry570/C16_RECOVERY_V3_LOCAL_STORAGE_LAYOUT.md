# C16 Recovery V3 — Local Bulk Storage Layout

## Purpose

The local/control host root filesystem has limited free space (~65 GiB), while `/root/share` has substantially more free capacity (~494 GiB at authorization time). All large recovery-v3 assets and returned raw data must therefore use `/root/share`, not `/workspace` or the local root filesystem.

This is a storage-placement change only. It does not change any scientific identity, runtime, model/scenario contract, or remote GPU capture path.

## Required local/control-host roots

Use:

```text
LOCAL_BULK_ROOT=/root/share/c16_recovery_v3
LOCAL_RAW_ROOT=/root/share/c16_recovery_v3/raw
LOCAL_MODEL_ROOT=/root/share/c16_recovery_v3/models
LOCAL_HF_CACHE_ROOT=/root/share/c16_recovery_v3/hf-cache
LOCAL_TRANSFER_STAGING=/root/share/c16_recovery_v3/staging
LOCAL_BULK_RECEIPTS=/root/share/c16_recovery_v3/receipts
```

The Git worktree may remain under `/workspace`; only compact code, manifests, receipts, TSV/JSON/MD publications, and tests belong there.

Do **not** place large raw traces, model weights, large archives, profiler databases, or transfer staging payloads under `/workspace`, `/root/.cache`, `/tmp`, or another root-filesystem-backed path when `/root/share` is available.

## First preflight before R1/R2/R7

On the local/control host, record:

```bash
readlink -f /root/share
df -B1 /
df -B1 /workspace || true
df -B1 /root/share
df -T /root/share
stat -f /root/share
mkdir -p /root/share/c16_recovery_v3/{raw,models,hf-cache,staging,receipts}
test -w /root/share/c16_recovery_v3
```

Create and delete a tiny sentinel file under `LOCAL_BULK_ROOT` to prove writability.

Record filesystem/device identity so the receipt proves that `/root/share` is not accidentally resolving to the same constrained root filesystem.

If `/root/share` unexpectedly resolves to the root filesystem or has <100 GiB free, do not silently fall back to `/workspace`; diagnose the mount/path first.

## Download/cache placement

For any exact-revision model download performed on the local/control host, set the cache for that process to `/root/share`, e.g.:

```bash
export HF_HOME=/root/share/c16_recovery_v3/hf-cache
export HUGGINGFACE_HUB_CACHE=/root/share/c16_recovery_v3/hf-cache/hub
export TRANSFORMERS_CACHE=/root/share/c16_recovery_v3/hf-cache/transformers
```

Place finalized exact-revision model assets under `LOCAL_MODEL_ROOT/<deployment>/<revision>/` or an equivalently deterministic layout.

Do not allow an implicit Hugging Face/model cache under `/root/.cache/huggingface` to fill the root disk.

## Rolling copyback destination

Every remote raw trace / large profiler payload copied back from the GPU server must land under `LOCAL_RAW_ROOT`, using a deterministic hierarchy such as:

```text
/root/share/c16_recovery_v3/raw/
  <deployment>/
    <scenario>/
      <phase-or-step>/
        <run_id>/
          <raw files>
```

The compact Git-side artifact index must reference these absolute local paths and include size/SHA256.

## Space guards

Before every model download and every formal-copyback batch, record free bytes on `/root/share`.

Recommended guards:

```text
LOCAL_BULK_MIN_FREE_BEFORE_NEW_MODEL = 80 GiB
LOCAL_BULK_MIN_FREE_BEFORE_CAPTURE_COPYBACK = 50 GiB
```

If projected copyback/download would violate the guard:

1. identify duplicate caches/staging files that already have final hash-closed copies;
2. remove only duplicate/staging data, never the sole hash-closed raw artifact;
3. compact/compress only when the parser/consumer contract already supports it;
4. recheck free space;
5. continue.

Do not redirect large data to the 65-GiB root disk as a workaround.

## Final acceptance

Recovery-v3 final closeout must report:

```text
LOCAL_BULK_ROOT=/root/share/c16_recovery_v3
LOCAL_BULK_FILESYSTEM_ID=
LOCAL_BULK_FREE_BYTES_FINAL=
ROOT_FS_FREE_BYTES_FINAL=
ALL_REQUIRED_RAW_UNDER_LOCAL_BULK_ROOT=true
ROOT_FS_LARGE_PAYLOAD_LEAK_COUNT=0
REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0
```

A scan for large campaign payloads outside `/root/share/c16_recovery_v3` must be performed at closeout. Legitimate compact Git metadata under `/workspace` is not a leak; raw/model/archive/profiler payloads are.
