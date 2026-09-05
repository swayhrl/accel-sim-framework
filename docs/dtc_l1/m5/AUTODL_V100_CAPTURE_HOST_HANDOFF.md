# AutoDL V100 capture-host handoff

Status: OFFLINE_CLOSED; WAITING_FOR_CAPTURE_HOST. SIM_HOST retains the one
persistent M5 Goal and all scientific Git history. AutoDL is a disposable
capture worker and must never create a scientific commit.

## Operational reuse, not old science

| historical asset | allowed reuse | prohibited reuse |
| --- | --- | --- |
| 3bed4970 preflight | single-GPU, CUDA/tool/data-volume checks | its binaries, traces, source IDs |
| 3bed4970 offload | rsync partial/append-verify and SHA receipt | its archive identity |
| M4A copyback verification | copyback sequence | CUDA 12.6/NVBit 1.7.6 payload |
| /root/autodl-tmp convention | candidate data mount after fresh df/write test | assumption it remains best/current |

## Two distinct remote checkouts

The remote command runs from M5_CONTROL_CHECKOUT, never from the tracer pin:

| root beneath fresh selected data volume | exact role |
| --- | --- |
| m5-control | active Framework final V100-ready commit: controller, sm70 builds, checkers, Paper10 manifest |
| tracer-pin | clean detached Framework 0db04452ec1c47630e4b08002067d82c6811e243; used only through --tracer-framework-src |
| sources/polybench, sources/spmv-wrapper, sources/parboil | fresh pinned source roots |
| m5-paper10-traces | capture attempts, immutable bundles, external archives and receipts |

Preflight requires exactly one CUDA-visible V100 (CC 7.0), CUDA 11.8
nvcc/ptxas, zstd, tar, rsync, git, build tools, a data-volume df and write
test. Select the larger persistent data mount based on fresh evidence.

## Exact BICG pilot command

The workload-conditional controller makes SpMV inputs deliberately unnecessary:

    cd <large-data-volume>/m5-control
    CUDA_VISIBLE_DEVICES=0 NVCC=/usr/local/cuda-11.8/bin/nvcc \
      util/dtc_l1/capture_m5_paper10_traces.sh \
      --polybench-src <large-data-volume>/sources/polybench \
      --tracer-framework-src <large-data-volume>/tracer-pin \
      --nvbit-archive <large-data-volume>/inputs/nvbit-1.8.tar.bz2 \
      --out <large-data-volume>/m5-paper10-traces \
      --workloads bicg --pilot-only

The expected states are CAPTURING -> CAPTURE_BUNDLE_PASS -> ARCHIVE_PENDING ->
ARCHIVE_PASS; transfer later adds TRANSFER_PENDING -> TRANSFER_PASS.
Resume archives a valid unarchived bundle, or transfers a valid unreceived
archive; it never repeats GPU capture solely because a later operation failed.

STORAGE_ADMISSION.json is required before any non-BICG workload. It binds the
BICG bundle ID and archive SHA, measured raw/grouped/archive bytes, working
headroom, safety factor, projected/free bytes, selected volume and PASS. The
projection is (raw + grouped + archive + headroom) x safety_factor.

Use util/dtc_l1/m5_autodl_capture_orchestrator.sh from SIM_HOST for
connectivity/preflight, roots, natural completion, rsync copyback, archive
SHA comparison, unpack, internal SHA revalidation and transfer receipt. Its
--dry-run is the no-host regression path.
