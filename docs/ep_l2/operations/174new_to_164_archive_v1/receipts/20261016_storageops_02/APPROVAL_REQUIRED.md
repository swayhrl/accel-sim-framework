# One remaining gate: exact archive write root

Please authorize `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02` or specify another exact absolute archive directory in the verified 174-new SSHFS namespace. It maps beneath export `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02` on 164.

V2 section 2.4 says: “只有已经明确证实该目录由用户授权用作独立archive root，才在该root下创建唯一新174new_archive/<run-id>并做一个几字节的可删除探针”. Existing directory naming and displayed FUSE mode 0777 are insufficient to infer that authorization. No target writes have occurred.

No SSH passwords, keys, repeated failed login, or source mapping information are requested: SSHFS read access and the actual Lane5 source route are now verified. No tmp_pack deletion approval is requested at this stage; exact packs must first undergo Git analysis, complete backup and hash readback before a later concrete deletion list can be submitted.
