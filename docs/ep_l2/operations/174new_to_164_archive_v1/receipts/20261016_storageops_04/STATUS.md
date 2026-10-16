# V5: BRIDGE_HANDSHAKE_COMPLETE_TARGET_READY_AWAIT_S01_READY

Authority: `011b827c6b686ff4cff0387cafc23977376698de`. The original Goal and execution branch continue. All Git pack sources remain SOURCE_KEEP; no new pack backup task is running.

The compliant bridge `/root/share/host174_storage_recovery_bridge/20261016_storageops_02` now exists. Target created the unique closed 8-byte nonce, source Ops independently matched its path/SHA256/inode/size at source commit `a279d7d2ac23db0c59c39031736e6618e2787fe6`, and the creator removed its nonce and READY marker. Target recorded exact-path absence in both namespaces; this is labeled as a target observation, not an independent source release receipt. Source must still perform its own ready-to-stage recheck.

An atomically published `TARGET_RECEIVER_READY.json` in that bridge references target cleanup commit `1376660991149fa50b63b3a63e1db06390c55548`, source independent PASS, the frozen source inventory hash, one-active-batch limit, <=512MiB, 30MiB/s and Share >=40GiB. The unique 164 root remains `/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02`.

Next: the existing old174 source Ops window stages S01 and publishes its atomic READY with exact source/bridge files, sizes and hashes. Target then receives it and publishes DEST_VERIFIED after full SSHFS close/reopen hashes. Only the source owner evaluates/executes eligible exact .vvp release. No duplicate source copier/deleter has been launched here.

S01: 52 .vvp / 418020580 B. S02: 50 .vvp / 403579225 B. Frozen 102-file inventory SHA256: `d34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7`. S01/S02 source staging, target copy, DEST_VERIFIED and source release are **NOT_RUN by this target window**. No source READY has been consumed yet.

36 prior pack archives / 12415140272 B remain preserved, not recopied. Their container-workspaces route is acknowledged noncompliant with V4. The old task-owned stage was verified empty and removed by exact paths. No Git pack is deleted or proposed for deletion in this phase. Full fsck timeout and unknown partial-pack recovery value remain recorded in revision 03.

**Actual source bytes released: 0. SPACE_NOT_RECOVERED.** The 48GiB floor plus 2GiB build growth remains unchanged; no archive count substitutes for live source df or Lane5 admission. Source-side further scratch review is recorded at `67b625bb43b69f4241fe4770fb58cd3a13c5020f` in gpu-l2-cache-verilog; target does not duplicate or broaden that source executor.
