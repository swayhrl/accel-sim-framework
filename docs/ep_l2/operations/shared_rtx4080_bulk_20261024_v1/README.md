# RTX4080 full-workload asset campaign: phase 1 checkpoint

This is an **in-progress scientific handoff**, not an assertion that the complete asset campaign is finished. Three full-application Vector objects are sealed on the real 164 share. The full-size PolyBench 3MM invocation has completed GPU capture and all-record semantic validation; its derived CPU grouping is being resumed in a new attempt after the original NAS pump self-throttled. No simulator or historical scientific Goal was run by this campaign.

## Public access and verification

Public root: `/root/workspace/assets/traces/rtx4080_sm89/bulk_20261024_v1`.

Independent command: `/root/workspace/assets/bin/trace-assets-rtx4080` with `list`, `show ASSET_ID`, `verify --all`, and bounded `restore ASSET_ID --dest ABSENT_PATH --max-bytes LIMIT`. It requires no EP activation. It distinguishes numerical status, producer semantic qualification, and consumer qualification; numerical/producer candidates have no automatic consumer or timing qualification.

The same three objects were independently read in full from `/tmp`, `/root/workspace`, and `/root/data`. All 146 declared members, 58,404,226 logical bytes matched their committed SHA256. A separate 17,101,720-byte restore, bounded at 64 MiB, verified every restored member and left the source intact. See the `PUBLIC_VERIFY_*` and `PUBLIC_RESTORE_QUALIFICATION_V1` receipts in the Native174 snapshot. The parent also independently verified the public interface from EP-MAIN.

Storage chain: 109 task-private SSHFS exposes only the new RTX subtree through `hrl174new`, whose verified NAS mount source is `admin-wcx@10.208.130.164:/home/shared`. Verification is full close/reopen through that mount, not a claim of native execution on 164. No NAS credentials were copied to 109. SM70 CURRENT/catalog/scientific trees were not changed.

## Frozen scope and scientific identity

The live table is `/root/data/shared_rtx4080_trace_library_20261024_v1/control/UNIFIED_SCOPE_STATUS.json`. V2 records source/version/implementation, source file identities, binary, full argv, working-directory policy, runtime data overlay, controlled environment, and declared input bytes/SHA. Reference/checker identity is recorded separately; unclassified input-file roles remain conservative. The former binary+argv identity remains a physical alias only. The 176-candidate duplicate audit found zero groups where different V2 scientific identities were collapsed.

At this phase the table contains 284 exact logical identities and all 231 CUDA/Poly native attempts. It preserves the official SDK 4.2.9 denominator of 82 programs, the original mapped CUDA Samples 11.8 denominator of 73 programs/103 invocations, Rodinia 3.1's 23 families/40 exact invocations, Rodinia 2.0-ft's separate 11 invocations, Parboil's 11 programs/25 official datasets, and PolyBench's 15 programs plus explicit repair variants. The 2022-source Vector object is explicitly a catalog extra; it does not inflate baseline coverage.

CUDA Samples 11.8's complete 205-program source denominator is an additional in-Goal extension, with the original 73 and additional 132 reported separately. Newly built programs awaiting a frozen finite/native queue remain pending; they are not completed coverage or permanent exclusions.

Actual generated array bytes are a separate qualification. The initialization audit found two clock-seeded and 23 implicit-C-RNG cases requiring actual HtoD snapshot evidence. Pending cases are routed to the special-input queue. The two already sealed SDK Vector manifests are immutable; a separate overlay records their unsnapshotted actual input-byte identity. Their numerical QA and producer integrity remain independently reported. No source seed rule is presented as proof that native/capture arrays were byte-identical.

## Ordinary producer and whole-application proof

Producer SHA256: `55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73`.

Contract SHA256: `97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184`.

Streaming validator v3 SHA256: `f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1`; it pins the frozen parser, binds executable to static map, checks all declared kernels/stats, every record, exact direct constant-bank offsets, one context/stream, CTA/warp coverage and terminal EXIT. Per-kernel warp state is released. CALL/RET, texture/surface, dynamic warp sync, graph/JIT/multiple-context and other unsupported domains remain explicit specialist targets. No missing callbacks or zero traces are silently accepted as API-only.

The v2 mapper skips a cubin only when `nvdisasm -json` independently proves zero executable SASS. Actual non-NOP JSON/PLR mismatches remain closed. A later ELF-symbol alias mapper qualification is under development; the old HOLD attempts and mapper are preserved.

GPU UUID is `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`. The ordinary profile's exact SM89 gate is a profile limit, not a general Ada hardware rule: same-major SM8.x library cubins may execute on RTX4080 and require their own loaded-code proof. Old SM70 traces are not relabeled as RTX4080 assets.

## Completed work and honest negatives

All 51 Rodinia native invocations finished: 12 upstream self-check passes, 38 execution-complete cases requiring numerical review, and one MUMmerGPU SIGSEGV. Four BFS and two nearest-neighbor cases subsequently received independent full-data CPU-reference passes; original receipts are preserved.

Parboil's complete official input set was recovered and SHA-pinned. Original 24 native cases gave 17 checker passes, four genuine BFS reference differences, one TPACF reference difference, and two SGEMM host SIGILL failures. A source-proven missing C++ `return true` was repaired in a distinct host-only SGEMM variant; both complete inputs then passed the unchanged reference checker. The late-arriving full stencil default input also passed. Kernel algorithms and official input sizes were retained.

PolyBench's original Gram-Schmidt rank-deficient initialization and original FDTD anomalies remain numerical negatives. Separate complete-size host/input repair variants are recorded separately and do not replace the canonical inputs. Original SDK histogram/scan failures and subsequent atomic/warp-sync/full-size variants likewise retain separate identities.

Full 3MM GPU capture: 93.5269 seconds, 354 MiB peak observed GPU allocation, three kernels, 3,072 CTAs, 24,576 warps, 55,590,912 SASS records and 1,777,336,320 active-lane instructions. All records passed v3; compressed raw files total 395,983,200 bytes. The original postprocessor was deliberately stopped after closed checkpoints when NAS/FUSE waiting fed back into a 1 MiB/s throttle. Its raw/validation/partial derived outputs remain intact. A new CPU-only attempt adopts each raw file by full SHA and reuses only checkpoint-declared, hashed closed shards. It does not repeat the GPU capture or mix writes into the old attempt.

## I/O, process and recovery contracts

All GPU work takes `/data/c16/locks/c16_gpu_campaign.lock`, observes resident ComfyUI identity, actual activity and memory headroom, and terminates only its own work on competition. No foreign GPU service was stopped. Attempts are exclusive new directories; no historical attempt is overwritten.

Native174 owns the dedicated RTX SOURCE/TARGET locks; 109 owns an additional local I/O lock. The private NAS pump is bounded at 15 MiB/s and is separate from SM70's transport locks. The v2 pump distinguishes local physical block pressure from its own FUSE stalls. An 8 MiB A/B test produced 3.79 MiB/s at the 4 MiB/s request and 7.29 MiB/s at 8; both full independent Native174 reopen SHA checks passed. A real interrupted prefix exited 99 and was rejected without COMMIT. The original pump/source and failed attempt are preserved.

The bounded postprocessor uses one XZ compressor, 64 MiB total partition buffers, bounded CTA buckets and stable external sorting. Qualifications cover 2D/3D CTAs, interleaved cross-bucket records, partial/zero masks, variable instruction counts, real constants, deliberate interruption/resume, byte equivalence against the reference, and full concatenated-XZ EOF/CRC. The source remains intact. No truncated capture can be marked complete.

Catalog objects are published only after sender closure, full member SHA, atomic COMMIT/rename and independent receiver reopen. Immutable catalog versions and the RTX-specific pointer preserve history. The finite scope overlay records PID/start ticks, a 24-hour deadline, explicit stop file and queue-terminal condition; it is not a permanent scanner.

## Evidence layout

`snapshot/109` and `snapshot/174new` preserve the phase's code and receipts. JSON files are deterministic gzip members; `SNAPSHOT_MEMBERS.json` records each original uncompressed SHA and byte count. These are checkpoint snapshots; the remote live scope and immutable NAS COMMITs are authoritative for later progress. Engineering-stage and channel qualification objects are explicitly excluded from workload counts.

All source/hot data remain KEEP at this checkpoint. No source was deleted or storage release claimed. Source/dependency/native evidence cold archives and the unsupported-domain extensions continue under the same campaign.
