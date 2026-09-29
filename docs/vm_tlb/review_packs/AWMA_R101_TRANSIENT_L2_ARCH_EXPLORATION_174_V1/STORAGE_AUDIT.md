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

## Later pressure handling during formal replay

Additional shared-overlay pressure occurred while B0/O1/M1 were running. The
following recoverable actions were taken without stopping any simulator:

- the R101 generated GPGPU-Sim build cache (206 files, 436 MiB) was copied and
  content/symlink verified at
  `/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/
  workspace_cache/gpgpu-sim-build`, then replaced by a compatibility symlink;
- three old unopened `/tmp` artifacts (338,158,201 bytes total) were copied to
  `storage_recovery/tmp_20260928`; their destination SHA-256 values match the
  recorded source hashes;
- six worktree `.orig` backups were copied with relative paths and SHA
  verification to `storage_recovery/worktree_orig_20260929`, then removed
  from the worktree;
- immutable shared Git pack
  `pack-2ada4af0f811168d5402be4cc6b58a25f06da3ac.pack` and its index were
  copied to
  `/root/share/mnt164/huangrulin/host174_storage_recovery/
  git_packs_20260928`, verified as
  `ec3162be1fb0495301e03bac4a86ed897417a096a22924d98036b8ca2b2c4d2b`
  and
  `4f13b7a6e90e69189f24808f7d04196ff98f0a8b8ead0a0485b5807f24c14518`,
  and replaced by symlinks. A real object from that pack passed
  `git cat-file`; branch/status operations continued normally.

These are host-storage operations only. Formal command receipts pin unchanged
scientific input, binary, library, source, configuration and tools.
