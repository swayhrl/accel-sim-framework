# BA independent postcopy SOURCE_KEEP reconfirmation

BA /root independently completed one bounded read-only review on original host `huangrulin-174`. Result: **PASS_OWNER_RECONFIRMED_SOURCE_KEEP**. Four AD_GEMM JSON source files (183,244 bytes) retain their original SHA256, dev/inode/size/mtime/ctime/uid/gid/mode/nlink. Three original directory records and their entries are unchanged. Five accepted-reference files remain byte-identical to original owner publication `75706e8a0e58309087c4eadb6280f7f3578bcb76` and its untouched scientific worktree.

Receipt: [BA_OWNER_POSTCOPY_SOURCE_KEEP_RECEIPT.json](BA_OWNER_POSTCOPY_SOURCE_KEEP_RECEIPT.json).

- Exact T request: [`aecccb6ad757a17c1c254940b01e11d56a6480a1`](https://github.com/swayhrl/accel-sim-framework/blob/aecccb6ad757a17c1c254940b01e11d56a6480a1/docs/ep_l2/operations/result_offload_pilot_20261023_v1/OWNER_POSTCOPY_HANDOFF_REQUEST.json).
- BA txid: `24b5cab04e21b55c269d15fce39746c03c4730159b24a2f5fd657ae687964a9c`.
- Target receipt SHA256: `db87833e52fd98c738a68e85591da3c70e2cb506f2c6fd7ffd495fe4bd27077d`.
- That digest covers the canonical inner `receipt` JSON plus LF, as defined by T. The complete Git file has a separate SHA256 recorded in this receipt. T's earlier transfer-stage proof and its later published postcopy proof remain separately identified.

SOURCE_KEEP continues: original paths stay authoritative, released bytes are zero, and no deletion or mutation is scheduled. This snapshot used read-only, no-follow, no-atime file descriptors, closed before receipt creation. Permission bits in T's records were explicitly normalized against the original full POSIX mode. There was no scientific Goal restart/reset, new simulation, historical test rerun, budget change, source release, target archive traversal or native restoration by BA. Existing accepted state is retained; F remains undetermined.

[verify_ba_source_keep.py](verify_ba_source_keep.py) is the exact bounded verifier used once for this authorized snapshot. It is not a periodic job. Its input is the privately retained exact GitHub response strings; those strings were compared byte-for-byte with the exact T Git objects before source access. SHA256 and Git blob identities of the published T inputs are included in the receipt. Do not rerun without an owner-authorized snapshot.

BA signs only the DTC-L1 four-file cohort. E2 must independently issue the EP-L2 receipt for txid `96202aab2446a3f6440108c045f524f9797a500c61446eeb7a52598c6ef37845`, target receipt SHA256 `7c429e019de4f1f1699abc61ca544542a3552ed8567923be15f02d1cb5936505`, using the same exact T request above. No E2 owner channel exists in this BA session, and no E2 delivery or signature is claimed. T retains resource accounting, workflow review and its final readback.
