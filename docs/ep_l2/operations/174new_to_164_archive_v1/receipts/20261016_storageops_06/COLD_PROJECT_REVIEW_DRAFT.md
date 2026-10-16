# Cold project release review preparation — no release approval requested yet

Source authority is the separate old174 Storage-Ops owner. Source audit and full path map are pinned in the adjacent SOURCE_* records. These are source allocation estimates, not measured df recovery; scientific data remains SOURCE_KEEP until complete destination and adequate recovery evidence plus explicit approval of the exact manifest.

| Priority | Exact old174 source | Archive suffix below authorized root | Directory-inclusive allocation upper bound | Current target evidence |
| --- | --- | --- | ---: | --- |
| R1 | /workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build | EP-L2/old174/workspace/repos/gpu-l2-cache-verilog-v3r1-clean/build | 4785803264 B | 12788/18565 files verified, 4247230942 B |
| R1R | /workspace/repos/gpu-l2-cache-verilog-v3r1r-clean/build | EP-L2/old174/workspace/repos/gpu-l2-cache-verilog-v3r1r-clean/build | 3594420224 B | Source manifests and batch plan only |
| R2 | /workspace/repos/gpu-l2-cache-verilog-v3r2-clean/build | EP-L2/old174/workspace/repos/gpu-l2-cache-verilog-v3r2-clean/build | 3459518464 B | Source manifests and batch plan only |

Authorized archive root on 174-new: `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`. All three source checkout Git directories, source RTL, tests, scripts and review packs stay on old174. The build trees include logs/generated RTL/historical scientific evidence; V5 scratch permission does not cover entire builds. Absence of readers at a bounded scan does not prove future consumer or registry closure. Exact toolchain/rebuild provenance is incomplete.

Default read-only R1 coverage/restore planning on 174-new:

```sh
A=/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02
python3 "$A/infrastructure/tools/v7_94d69d45d9ce/cold_project_restore.py" \
  --map "$A/infrastructure/project_manifests/SOURCE_MAP_63c243e.json" --project R1 \
  --source-manifest "$A/infrastructure/project_manifests/R1_8556dd125ac2.jsonl.zst" \
  --expected-manifest-sha256 8556dd125ac2147ccd035419a905093a20d56be989890f70a3193813ab3791e5 \
  --file-metadata "$A/infrastructure/project_manifests/R1_FILE_METADATA.jsonl.zst" \
  --expected-file-metadata-sha256 9226c1f5e457a8ab716afd08dc126201f94a827afde1e4312b4a1f8bf936d22f \
  --receipt "$A/receipts/R1_B001_DEST_VERIFIED.json" \
  --receipt "$A/receipts/R1_B002_DEST_VERIFIED.json" \
  --receipt "$A/receipts/R1_B003_DEST_VERIFIED.json"
```

The command reports incomplete coverage. The tool refuses restore execution until complete coverage and writes only a fresh independent target-side test directory. Numeric file metadata is retained in a separate SHA256-pinned sidecar; the current restore planner joins every row to the frozen file hash/identity and reports complete recorded metadata, but does not apply ownership/mode or claim native metadata restoration. A tested reverse bridge handoff and old174 source-owner import into an absent sibling `build.restore.from164`, full hash and permission checks, and approved promotion are still required before publishing a source restore execution command. The withdrawn direct SSHFS-to-old174 /workspace command must not be used.

Approval package pending: complete batch receipts, full scope mapping and compressed manifest SHA256s, adequate restoration evidence, current source consumer/owner clearance, exact per-file release list, and allocation versus actual-df measurement plan. No project currently qualifies as READY_FOR_USER_APPROVAL or RELEASE_AUTHORIZED.
