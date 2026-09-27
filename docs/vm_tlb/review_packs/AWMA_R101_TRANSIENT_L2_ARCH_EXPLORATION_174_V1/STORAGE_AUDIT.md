# 174-new local storage audit

The user authorized migration without interrupting current programs.

Read-only audit found `/root` used about 35 GiB. The largest unsafe-to-move
paths were the active C16 worktree/binaries, `.vscode-server`, the primary
repository, `offline-sim-v1`, and the current R101 build runtime. These remain
untouched.

Four completed AWMA runtimes had no open file handles. Each was copied to
node164, checked by checksum dry-run and file-count equality, then its original
directory was replaced with a compatibility symlink:

| original path | durable node164 path |
|---|---|
| `/root/awma_rtx4080_requal_mechanism_v1_runtime` | `/root/share/mnt164/huangrulin/archived_runtimes_174new/awma_rtx4080_requal_mechanism_v1_runtime` |
| `/root/awma_native_simulator_cross_calibration_v1_runtime` | `/root/share/mnt164/huangrulin/archived_runtimes_174new/awma_native_simulator_cross_calibration_v1_runtime` |
| `/root/awma_prel1_coalescing_v1_runtime` | `/root/share/mnt164/huangrulin/archived_runtimes_174new/awma_prel1_coalescing_v1_runtime` |
| `/root/awma_bottleneck_observatory_v1_runtime` | `/root/share/mnt164/huangrulin/archived_runtimes_174new/awma_bottleneck_observatory_v1_runtime` |

The original paths continue to resolve through symlinks. Recovery consists of
copying the node164 directory back; no artifact was discarded. Root free space
rose from 7.7 GiB immediately before migration to about 11 GiB afterward.
