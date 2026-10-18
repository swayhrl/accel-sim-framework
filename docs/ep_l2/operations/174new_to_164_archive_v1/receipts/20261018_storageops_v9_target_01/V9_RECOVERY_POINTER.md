# V9 recovery pointer

Target archival and protocol work is complete. C2P1/C2P2/M2D originals remain SOURCE_KEEP; this pointer grants no source deletion or Lane execution.

Core Framework commit: `4b86a5492ad5d7928d2d6e0d9b251b874727f7da`.
Repository `swayhrl/accel-sim-framework`, branch `hrl/ops-174new-164-archive-exec-v1`.
Use only genuine164 SSHFS `admin-wcx@10.208.130.164:/home/shared` on174-new. Native164 paths start `/home/shared`; the same mount pathname on old174 is misleading.

Publication proof: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/TARGET_V9_CONTROL_4b86a5492ad5_PUBLICATION.json`, SHA256 `b458290dba2c6d22bb2df7c9b0da5f6e76ec426787330306aa61f3bd4869936b`.

Source-owned R2 release measured +2,689,970,176B at that instant. New cold archive1,257,838,483B is separate and is not source free space.

Exact current recovery records (all hashes refer to complete file bytes):

- SOURCE_TO_164_INDEX_V9.json: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/4b86a5492ad5__SOURCE_TO_164_INDEX_V9.json`; SHA256 `9cd67773c98914e8c24c3aad62d9b8c517a91a633f99edcc6e9b3be47b8695fb`.
- V9_ARCHIVE_RECEIPT.json: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/V9_ARCHIVE_RECEIPT.json`; SHA256 `03f5ab9869ad58d5b165682dda885e0c269913ba99a44784b4f6e64342520f3c`.
- V9_RESTORE_RECEIPT.json: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/V9_RESTORE_RECEIPT.json`; SHA256 `c79d8c8786f946d5bfa90d786a3dbe8c2bd128e0823eab2063f181ae92bdbf55`.
- V9_SPACE_BEFORE_AFTER.json: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/V9_SPACE_BEFORE_AFTER.json`; SHA256 `5b84b4107945e6891f1c4ecf745a0bd3c4f7192b696ae7a737fa33eae7d3b117`.
- V9_OPERATOR_RECOVERY.md: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/4b86a5492ad5__V9_OPERATOR_RECOVERY.md`; SHA256 `8eee945ab3f2e4ccf2150a866635410bc850437a2ee1de6cab16f54f15c89474`.
- V9_PROTOCOL_TEST_RECEIPT.json: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/4b86a5492ad5__V9_PROTOCOL_TEST_RECEIPT.json`; SHA256 `4866d97c3732ae1af29a093c34d86ee35a29968f104f08465cca0a273a4d9dec`.
- V9_FUTURE_EXACT_PER_FILE_RELEASE_PROPOSAL.jsonl: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/V9_FUTURE_EXACT_PER_FILE_RELEASE_PROPOSAL.jsonl`; SHA256 `f535e6be64877948b757e13681a93ab7a67b690ff7ee0d27190e2219a02061b4`.

Project source -> exact data roots:

- C2P1: `/tmp/c2p-gpgpu-pre-attribution-20260822/build` -> `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/C2P1/old174/tmp/c2p-gpgpu-pre-attribution-20260822/build/d07ad19814f68aeb53eecbc76a4896898ed2af30bf2196348117a8680c195048/tree` (native164). Manifest `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/C2P1_V9_TRANSACTION_MANIFEST.json`, SHA256 `aea889b2477a0b0d43a819565667e622253e52447d43f4f600236bf2f63f12b1`.
- C2P2: `/tmp/c2p-gpgpu-build-20260821/build` -> `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/C2P2/old174/tmp/c2p-gpgpu-build-20260821/build/cd1ea5b35dd161ea42981d8d7d2864b6e1a6b7a0cf848ecaa396b5395ed3806d/tree` (native164). Manifest `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/C2P2_V9_TRANSACTION_MANIFEST.json`, SHA256 `0e8a85e71d224771451fab43c077e49b98350aac808a50ef2faf40f69404fc19`.
- M2D: `/tmp/m2d-core-g21/build` -> `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9_cold_source_01/M2D/old174/tmp/m2d-core-g21/build/9b7971a8bd636476465d5d92fb8330d8502e1c5e775fb7bb8c29cab47ed06779/tree` (native164). Manifest `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/M2D_V9_TRANSACTION_MANIFEST.json`, SHA256 `5d534d5a9e19d7fff11b4938f51149ee384f8e345c675331b0c361a8f5b29541`.

Preserved tool directory on174-new: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261018_v9/tools/v9_6fd13ab5a9df_td90381f1cfcf`; `v9_transaction.py` SHA256 `6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe`.
Follow the exact operator guide above: verify manifest SHA, choose a NEW ABSENT native destination, run native_restore and verify UID/GID/mode/mtime and directory metadata. ctime is provenance only. Old174 access requires the sole <=256MiB reverse bridge; never overwrite an existing original or bypass current floors.
Complete content verification covers all615 files. Actual native proof covers11 representative files and42 directories, not a full615-file native import. All source permission/release decisions remain with the source owner and new exact user authorization.
No historical36Git pack or35PolyBench migration was repeated; R13/V8 evidence and scientific assets remain preserved.
