# 174 -> 164: C16 model-dual-copy recovery audit and second-candidate triage

Date: 2026-10-19; status **READ_ONLY_PROOF_ONLY — no transfer or release authorization**.

## Why this next step
Source census: Framework `474dc4613c6bd65de9431198caf9263df67dac7a`, `docs/ep_l2/operations/global_cold_census_20261019_source/`.
Target prior-index review: Framework `76ef35b7b9b70590b6c69e01b15609dd39131413`, `docs/ep_l2/operations/164_existing_archive_review_20261019_v1/`.

At 2026-10-19 11:41:36 UTC original 174 native `/workspace` had `f_bavail=13,702,602,752 B = 12.762 GiB`, /root/share `44,375,302,144 B`. These are historical; not current admission.

C16 original source inventory `SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json` maps **exactly six historical SHA-bound weight shards** (Qwen2.5-7B-Instruct RAW 4 shards, AWQ 2) between:
- `/workspace/c16_assets/c16-a/metadata/Qwen__.../` canonical local model roots; six distinct regular files, source-side st_blocks **20,802,158,592 B ≈19.373520 GiB**.
- `/workspace/c16_exchange/autodl_wave1/outbound/C16_GPU_PACKAGE_P2_168c9714/models/...` and `C16_GPU_PACKAGE_P3_168c9714/models/...`; six distinct regular files, outbound st_blocks **20,802,138,112 B ≈19.373501 GiB**.

Two six-file sets are *separate* original174 inodes with nlink=1; original size and historical SHA receipts agree. **The 12 file bytes have NOT been freshly hashed or verified to match in the current census.** No already164 matching archive/native restore receipt was found within V9/TLS indexes. Sum **38.747 GiB is an upper bound on visible allocated source bytes, not proven unique/releasable or a promised `df` gain**.

Original 174 C16 asset supervisor PID280466 was alive with a LOG FD; this does not prove a future package/model reader is absent. A source owner/transfer queue review is mandatory. Do not kill, stop, reconfigure or disturb supervisor or other C16/109/164 tasks.

*Project policy context:* 164 is the intended durable model authority; 109 may host an active replica; an original174 model/path is not disposable merely because 164 exists. Only **matching exact per-file identity plus future-consumer/owner clearance** can release an original file. Model asset project lineage and future uploads may still use the P2/P3 outbound package. Preserve code, original manifests, metadata/provenance and packaging scripts.

## One-pass decision tree

### Phase 1 (NOW, fully read-only / metadata-first; parallel windows)

1. ORIGINAL174 owner/provenance audit: validate the exact12 regular-file identities (dev/inode/nlink/size/mtime/ctime, expected historical SHA), package P2/P3 materialization receipts, model immutable source receipts; check C16 authoritatively frozen RUN/CAPTURE/upload/asset-supervisor queues, old174/109/164 intended readers, scripts and planned transfers. Explicitly decide per six-file *set* `PACKAGE_REQUIRED`, `MODEL_SOURCE_REQUIRED`, `COLD_OWNER_CANDIDATE`, `UNKNOWN`, and proof of why. Do not infer from zero FDs or old September dates. Do **not** hash all12 by default; confirm content on the required six streams after eligibility established.
2. TARGET174-new true164 owner: first map SHA+filenames+model revision from existing C16 authority indexes to **bounded exact known paths**, no NAS-wide search. If a candidate native164 file is found, independently verify current full bytes SHA256 for six distinct contents once, file size/UID/GID/mode/mtime and whole-original recoverability; reconstruct two original layouts in absent native destination(s) only if such an operation is separately authorized and doesn't conflict with active source/model authority. In this Phase 1, inspection and bounded hashing of existing exact, inactive files is allowed under IO/lease check; **do not start recovery writes, allocate a second 20GiB model tree, transfer, delete or overwrite**.
3. A second ORIGINAL174 read-only small-path triage checks the **16.472 GiB Legacy_VM_GPU**, **15.809 GiB Other_tmp_scratch**, and nonprotected portions of **30.446 GiB Other_legacy_GPU_and_unresolved**. Depth2/3 within frozen top roots only; exclude every EP-L2/DTC-L1 trace dependency and hardlink alias, currently active C2P/TLS offloader and scientific inputs. Identify at most 3 disjoint groups of >=2GiB with strong prior recovery/rebuild/provenance potential; unknown inputs HOLD. C2P=LOW priority. Do not rescan 2.3M entries or `du /`.

Source and Target continue concurrently at metadata level. Neither needs to wake old blocked TLS B0010 or acquire its sender/receiver. Avoid high-IO checksum scans while EP-L2 new A–E is building or otherwise holds resources; coordinate read bandwidth and use one bounded source audit. Archive work is not authorized by the old TLS-specific16GiB override.

### Phase 2 (not authorized in this contract; prepare conditional routes)

**Route ZERO-TRANSFER** if a durable true164 model authority contains all six byte-identical shards: pin existing-native source, full six SHA, original pair hashes+metadata, and perform separately authorized independent native full-file restore of original logical layouts (could use content-addressed deduplication, but need verified reconstruction of both original layouts, including metadata). Then prepare TWO independent exact source release selectors (six outbound package shards; six original174 model-cache shards). They have different owners/consumers and must not be bound by one blanket delete. Preserve manifests/code and clear any runtime assumptions before deleting.

**Route ONE-TRANSFER** if no true164 authoritative six-file set exists: choose one of the verified original174 sets as source, verify all six current SHA and planned owners, and propose a single-stream, resumable 164 transfer of *six unique contents* rather than copying both duplicate sets. Store two original path/metadata manifests for complete reconstruction. Use exact absent 164 destination, independent full native restore, no source overlay payload staging, <=256MiB physical Share bridge, <=30MiB/s, one sender/receiver, close/reopen SHA and byte-identity. Requires a **new, separately user-approved C16-only low-workspace COPY_ONLY policy** (the original 48GiB applies; TLS16GiB and P9 exact release may not be borrowed). C16 owner must sign off on both incoming/outgoing transfer and package-path disruption.

For either route, actual ORIGINAL174 scientific *source release* is **not authorized** by this contract. After true164 SHA+native restore, and owner/scheduled-reader clearance, submit two separate SHA-frozen exact 6-file release proposals and a one-time low-disk source release resource gate/qualified crash-safe journal for user approval. If package still needed, release only the independently approved safe subset after complete proof. Never delete a source tree, package receipts, working scripts, model metadata/catalog, code, Git, shared trace, EP-L2/DTC-L1 or C16 active originals; no symlink substitution or silent path rewrite.

Potential upper bounds from the historical source st_blocks: outbound only 19.3735GiB; both6-file sets 38.7470GiB. Baseline free12.762GiB would hypothetically become ~32.135GiB or ~51.509GiB, **if** all those blocks were genuinely exclusively reclaimable and no concurrent writer consumed space. Actual immediate before/after `f_bavail` is the only source reclamation measurement. EP-L2 normal workspace science floor remains48GiB, so outbound-only is insufficient, both sets (if valid) leave little headroom; second legacy/scratch shortlist is worthwhile in parallel.

## Strict isolation

- Protect entirety of EP-L2, DTC-L1 and their cross-project dependencies, plus all current C16 authority/master assets until separately released. No raw deletion/migration of shared traces.
- No old Lane5/R19/TLS B0010/archived nine windows restart or rerun, no new long-lived watcher, no extra GPU tasks, no resource-floor relaxation; no unbounded source/NAS scans.
- Run the current phase as finite bounded read-only Code/metadata inspection and report publication only. All current/releasable bytes are **0**.
- Ordinary parsing/index problems solve and continue within scope. Owner ambiguity/mtime or SHA drift, future consumer, source/target uncertainty, missing provenance, or resource pressure are exact item-specific HOLD. Do not spend hours perfecting low-value metadata.
- Outputs: `C16_SIX_SHARD_OWNER_AND_FUTURE_USE.json`, `C16_DUAL_COPY_EXACT_IDENTITY.csv`, `C16_164_AUTHORITY_SHA_MATCH.json`, `SECOND_GROUPS_SHORTLIST.csv`, `STORAGE_NEXT_AUTHORIZATION_PROPOSAL.md`, small SHA-bound remote-readback receipts. Read-only results from distinct branches can be joined by immutable SHA. No claim of restored/released files while there are none.
