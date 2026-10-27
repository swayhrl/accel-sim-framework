# Scan M16 engineering-negative verifier V2 — read-only transport inode policy

Implementation `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/scan_m16_diagnosis_v1/terminal_verifier_v2/scan_m16_terminal_verifier_v2.py` SHA **118ef13d04f2c77ac488395aeb775d3e4df1dbb72b05e1ed451156de0440e78e**. Native CPU qualification: **10 tests PASS**. Real preserved bundle read-only verification: **VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED**. No old source, manifest, selector, certificate, archive, native restore, registry or controller was modified. No model or signal was started. Main alone decides any new configuration integration.

The preserved V1 verifier remains HOLD at its exact full-manifest equality check. Its observed failure is recorded in `OLD_V1_READONLY_HOLD.json`; this package does not claim the V1 verifier passed.

## Observed discrepancy

Eight entries added to the archive from true164 `bundle/context` now have different transport inode numbers. Original source native entries, file bytes/SHA, dev/ctime/nlink/allocated/mode/uid/gid/size/mtime/type/path, original 47 source pins, archive chunks and complete native2128 restore are unchanged. `ACTUAL_READONLY_VERIFY.stdout.json` records every original/current inode before and after verification.

This observation is compatible with SSHFS virtual inode renumbering. It does not prove a physical remote inode change or data corruption. V2 declares a **narrow, explicit logical identity rule** for these eight added transport entries; it is not a general filesystem exemption.

## Exact policy

- Only the preserved transaction `1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f` and exact true164 source `admin-wcx@10.208.130.164:/home/shared` are eligible.
- Only `_ENGINEERING_CONTEXT` itself and its seven fixed original context filenames may vary in **inode**.
- Every other transport field remains exact, including **dev, ctime, nlink, allocated, uid, gid, mode, size, mtime, type, path and regular-file SHA**. Missing/extra/renamed entries, links, and unknown fields fail closed.
- **All native original entries retain every lstat field and content SHA**, including inode. The preserved source checker rehashes the complete native original tree and rechecks source pins before/after.
- Original stored manifest/selector/certificate/archive-index/COMMIT/receipt stay byte-for-byte sealed. V2 does not normalize or rewrite them. Original old selectors continue to govern archive verification and full native restore.
- Fresh native boot/namespace/device, true164 mount, exact context path and no-symlink ancestry are verified. Full archive chunk SHA, complete native restore bytes/numeric metadata, all gzip CRCs and two real no-hole process-departure scans remain required.

## Compatible API

```python
module.verify_bundle(bundle_path, expected_self_sha="118ef13d04f2c77ac488395aeb775d3e4df1dbb72b05e1ed451156de0440e78e")
module.verify_certificate(certificate_path, expected_self_sha="118ef13d04f2c77ac488395aeb775d3e4df1dbb72b05e1ed451156de0440e78e")
```

Return status remains `VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED` with unchanged cohort/UUID/certificate SHA, accepted_cyclesNone/performance_acceptedFalse, no execution receipt and original spent1/refund0. Additional provenance includes:

- `verifier_schema=SCAN_M16_ENGINEERING_NEGATIVE_VERIFIER_V2`
- new verifier source path/SHA and pinned original producer source path/SHA;
- `original_v1_verifier_pass_claimed=False`;
- explicit exception policy and per-entry original/current transport identity observations;
- all preserved original seal SHAs and original selector.

The preserved certificate remains `37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7`, manifest remains `53f568eb41910b6ec83785ca9e3b4446381d3d9ac09ffe3207df3e1d49aa344d`. No new certificate or terminal result was emitted.

## Validation and integration boundary

CPU tests cover context-only inode changes accepted; native inode/dev/ctime and other original metadata changes rejected; every non-inode context field, content SHA, path/type, missing/extra members and selectors rejected; old/new source drift and sealed manifest/certificate/archive drift rejected; low-level archive chunk-byte and native restore content/mode tampering rejected.

Main must publish a distinct versioned verifier/config source pin if adopting V2. Existing V1 config remains honestly HOLD; this agent has not replaced it, registered an R2 trial, projected a new RESULT, or changed the 350-cell statistics.
