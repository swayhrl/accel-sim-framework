# AWMA Discussion Reference — storage governance, GPU side lane, consumer audit, and 174 local storage inventory

Date: 2026-09-17

## 1. Scientific state after Q05 translation timeline closure

The Q05 timeline stage completed with timing-neutral diagnostic telemetry. The actual translation key is `{asid, vpn, page_size}`.

Observed timeline facts:

```text
10k:  19 keys / 19 fills / 106 merges / 8,730 post-fill REQUEST invocations
50k: 104 keys / 104 fills / 374 merges / 474,414 post-fill REQUEST invocations
full: 240 keys / 240 fills / 393 merges / 8,747,322 post-fill REQUEST invocations
full natural R0 = 885,681 cycles / 224 CTA
```

The result remains `MIXED`.

Supported:

- burst fanout before fill is real;
- new translation keys continue well beyond the earliest window;
- substantial post-fill activity exists;
- a simple TLB-capacity/thrashing explanation is not supported.

Still not claimed:

- `REQUEST` is not memory-instruction coverage;
- post-fill L1/L2 outcome was not directly logged;
- no mechanism speedup follows from the timeline alone.

The main scientific line remains paused before mechanism testing while infrastructure and evidence preparation proceed in parallel.

## 2. Storage role

AWMA's long-term storage topology is:

```text
109 = GPU producer / short-lived staging
174-new = simulator / analysis / worktree host
164 = durable large-data authority
```

Large artifacts such as model assets, simulator-native traces, NVBit/NSYS/NCU raw, full simulation raw, cycle timelines and large derived datasets belong on node164.

Existing accepted historical paths are provenance and are not mass-moved for neatness.

## 3. Producer/consumer storage closure

Node109 Track C proves producer-side finalize/publish/ACK and then performs bounded selected-kernel captures.

Node174-new Track D independently proves consumer-side read-back/provenance/catalog consistency.

Track D has completed its independent existing-data work and is now correctly waiting for the Track C producer canary receipt/ACK rather than inventing one.

When that receipt appears, Track D needs only a delta closeout, not a repeat full audit.

## 4. Why local 174 storage still needs a separate audit

The durable-consumer audit answered a different question:

> Are accepted AWMA large artifacts durably available from node164 without depending on 174-local authority?

It did **not** fully answer:

> What is physically consuming the nearly full local/host-backed filesystems visible from 174-new, and how much can later be safely reclaimed?

These must be separated because `no local-only authority` does not imply `no large local working copies`.

174-new may still contain large:

- historical simulation outputs;
- build trees and binaries;
- Git worktrees;
- caches;
- temporary logs/raw copies;
- data belonging to other research lines sharing host-backed mounts.

Therefore Track E is a read-only capacity and retention-semantics audit.

## 5. Why Track E must understand mount topology first

Paths such as `/`, `/root/data`, `/root/share`, and `/root/share/mnt164` may refer to different or overlapping physical filesystems.

A naïve recursive `du /root` could:

- count node164 remote durable data as local usage;
- double-count bind mounts;
- traverse other remote filesystems;
- produce a misleading reclaimable-space estimate.

Therefore Track E must first establish filesystem/mount identity and use one-filesystem inventory semantics (`du -x`, `find -xdev`, or equivalent) before drawing capacity conclusions.

## 6. Cleanup classification discipline

Track E must classify rather than delete.

Important statuses include:

```text
KEEP_ACTIVE
KEEP_REPRODUCIBILITY
KEEP_SHARED_OTHER_PROJECT
WORKING_COPY
CACHE_REGENERABLE
BUILD_REGENERABLE
DUPLICATE_VERIFIED_ON_164
SAFE_CANDIDATE_AFTER_ACK
UNKNOWN_REVIEW_REQUIRED
DO_NOT_TOUCH
```

A local file is not safe merely because a similar filename exists on node164. A verified duplicate requires artifact/provenance identity, durable path, size/hash/manifest closure, and no local-only uncommitted metadata.

Similarly, an old worktree is not disposable merely because its branch is old. Dirty worktrees and worktrees tied to other active research lines must be protected.

## 7. Why no deletion is allowed yet

This audit is intentionally read-only because a storage cleanup command can destroy more provenance than a failed experiment.

No deletion, `git clean`, `git gc`, worktree removal, cache purge, compression/replacement, or mass move is authorized.

The audit should instead produce:

```text
what occupies space
what is definitely keep
what is high-confidence cleanup candidate
what is unknown
conservative reclaimable bytes
upper-bound reclaimable bytes
```

Only after ChatGPT reviews that list should a separate cleanup stage be issued.

## 8. Current GPU side lane remains independent

Node109 Track C is already active and may continue its storage-qualified bounded simulator-native capture of the four accepted Qwen2.5 targets.

Track E must not interfere with GPU work, Track C storage publication, or Track D's waiting state.

## 9. Current scientific STOP boundary

Do not use this infrastructure window to drift into mechanism experiments.

Not yet authorized:

- L2-TLB latency/PTW/walker/capacity/page-size/Segment sweeps;
- new TLB/cache mechanisms;
- SIM_INPUT admission or simulation of new Track C captures;
- arbitrary NCU/C16WARP1/Qwen3/DeepSeek campaigns beyond current Track C authorization.

After Track E returns its storage inventory and Track C continues, the conversation returns to the Q05 scientific main line.
