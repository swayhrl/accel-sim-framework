# AWMA Current State

## Coordination source anchors

This AWMA coordination branch is created from canonical C12–C15 inheritance commit:

```text
7b6f2b88c36b4ed1bbdcd72761063f881c7b6c96
```

That inheritance result is:

```text
C12_C15_174NEW_INHERITANCE_PASS_REPLAY_ENVIRONMENT_BLOCKED
```

Meaning:

- historical C12–C15 scientific assets are now indexed/canonicalized for 174-new/node164 use;
- C12 formal baselines, C13/C14 diagnostic boundaries, C15 static boundary, raw/derived lineage and Git authority are preserved;
- exact historical simulator runtime replay is not closed because the exact historical Core/binary and local nvcc are unavailable;
- current C16 MREF-sharded data is not proven lossless for Accel-Sim traceg conversion.

## Node roles

### 109 / RTX4080

Current role: Producer/capture.

Known formal capture architecture:

- `MREF_SHARDED_COMPLETE_SET`
- binary format `C16WARP1`
- Pipeline-V1 ACKed transfer
- native/offline evidence only within the accepted scope

Current/known active formal-capture branch family includes:

```text
hrl/c16-qwen0-decode-formal-109-v3
```

At the time this handoff is written, its known pushed commit is:

```text
20ee2e015d3b3eb72b67d03657242887932a925d
```

Do not assume unreviewed follow-on branch state has been integrated into this AWMA coordination branch. Consume it by explicit commit/manifest evidence when needed.

### 174-new / port 2239

Current role: Ingest/analysis/catalog and future simulator-analysis owner.

Historical C12–C15 canonical inheritance is complete enough for analysis continuity. New simulator runtime remains to be established as a maintainable baseline rather than relying on an unrecoverable historical binary.

### node164

Canonical long-term root remains:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

The path is not renamed. AWMA metadata will make the logical project identity explicit.

Historical simulation namespaces already exist beneath this root from the inheritance stage.

## Current Native Evidence status

Accepted facts:

- C16WARP1 is suitable for scoped real-GPU address/page/cache-line/per-MREF analysis.
- C16WARP1/MREF sharding does not preserve enough information to claim cross-MREF global temporal order or whole-kernel reuse distance.
- first formal Qwen0 Prefill Attention/GEMM complete sets were ingested on 174-new and exact producer/consumer count closure passed.
- object attribution across replay processes requires same-process address context or equivalent normalization; do not join absolute object maps across unrelated CUDA processes.
- byte width/access kind must remain UNKNOWN when not represented/proven; never default to WRITE.

## Current Simulation Evidence status

Historical assets are available for reference/regression, but future simulation should use a new maintainable baseline.

Known gap:

```text
current C16 MREF-sharded/JSONL
    != proven lossless simulator input
```

Future simulator-compatible capture must preserve or produce enough semantics for faithful instruction/warp/coalescing/order/control reconstruction.

## Immediate AWMA execution order

1. Establish unified AWMA identity/evidence/catalog foundation on 174-new.
2. Backfill existing C16/historical assets through adapters without raw-data renaming.
3. Freeze machine-checkable Native/Simulation/Cross-view schemas.
4. Freeze `SIM_COMPAT_CAPTURE_V1` acceptance contract.
5. Attempt bounded new simulator-baseline bring-up where local toolchain permits; otherwise close the exact blocker and prepare the next wave.
6. Only after this foundation is accepted, run the next parallel wave:
   - 109 simulator-compatible capture implementation/canary;
   - 174-new maintainable simulator baseline qualification.

Do not divert into AWQ/raw7B/model expansion solely because this project foundation is being established. Existing workload campaigns continue according to their own accepted handoffs.