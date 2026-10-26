# SM70 V12R2 failure diagnosis and private V13 candidate
The original source, old runs, original frozen manifest, scientific registry and production locks were not changed. This task did not start a new archive hash, chunk hash, transfer, GPU job or simulation. Only small metadata, code and logs were read. Finite CPU fixtures created and reaped their own tiny pipe-test children.

## What is established
The V12R2 supervisor and driver are absent and terminal state is ATTENTION_RETAINED_NO_PUBLICATION. No target COMMIT or EXACT_BATCH_COMPLETE exists. The received exception is Source EOF before complete verification.
The old source proof binds FUSE inode96999419. The observed source inode is now97510165; path and all other stored metadata remain equal. V12R2 rechecks the old inode in the newly spawned source child AFTER a long retained-chunk hash pass. This is a strongly supported present predicate failure. The exact historical source stderr/rc was not persisted: exact() raised and finally closed stderr without reading it. Therefore the inode explanation must not be reported as the uniquely proven historical cause.

The frozen control flow reached the framed receiver loop after the mandatory existing-range SHA checks; this supports a completed V12R2 range-read pass, but no independent durable per-range R2 witness exists. The candidate keeps the next run's strict full range reread.

Metadata inventory:8587 closed ranges,611552641085 bytes,5606 complete member range coverages. Tree:944 closed files,317055807712 bytes;4662 members/294496833373 bytes remain to assemble. No current tree .writing file was found. These are metadata observations, not fresh body rehashes. Existing bytes can be reused; after a valid source EOF proof there should be zero missing payload ranges to retransmit.

## V13 narrow changes
Only the exact approved polybench NAS archive path and frozen whole SHA may use inode-tolerant comparison. Every other metadata field, including size, mtime_ns, ctime_ns, dev, uid, gid, mode, nlink and regular-file type, remains exact. Genuine164 source+fstype is checked. Context binds the original manifest SHA and original17.94GB whole-SHA proof. General same_source and nonarchive source_send still require exact inode.
All three archive identity gates (before stream, during stream, after final close) use this narrow predicate. The original full physical EOF, entire compressed-archive SHA, all5606 member whole SHA/order, chunk SHA and assembled closed/reopened whole-file SHA remain mandatory. Metadata is not a replacement for source-byte qualification.
A real qualified metadata preflight runs before the retained611GB range scan, and source startup refreshes its inode observation afterward. The scan itself is NOT skipped.
Sender stderr is continuously drained from each Popen into a bounded last64KiB capture plus8KiB read buffer. Return code and captured stderr are included on protocol EOF/nonzero exit. stdout framing and payload protocol are unchanged. The capture reports truncation and drainer state explicitly.

## Validation and Root decision
63 CPU positive/negative checks passed, including every stable metadata field, wrong mount/path/source SHA/frozen manifest/proof bytes, missing context, strict general inode behavior, AST preservation of the NAS-only write audit and byte-verification helpers. A real300023-byte stderr producer exited2 with no deadlock; the retained tail was bounded64KiB and all fixture children were reaped.
candidate_v13 contains engine, driver and supervisor, repinned consistently. ROOT_APPROVAL_TEMPLATE_V13.json is deliberately not an executable approval. No ROOT_APPROVAL.json exists and nothing was launched. Root must independently review the minimal diff, freeze a code CAS, create fresh exact approval and recheck ownership before finite NAS-only continuation. Keep every old failed run and original source.
