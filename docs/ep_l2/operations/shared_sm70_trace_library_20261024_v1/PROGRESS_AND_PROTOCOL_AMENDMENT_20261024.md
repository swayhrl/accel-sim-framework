# Shared trace library: current implementation and protocol amendment

The user expanded the active Goal to collect every missing usable RTX4080 trace,
validate simulator semantics, and resolve resource constraints in parallel.
The former onboarding restriction and original no-capture Goal wording do not
describe this later authorized scope. Historical scientific cohorts are unchanged.

## Content audit checkpoint

- Original174: 17,224 exact frozen file identities have SHA evidence; native174-new:
  8,684. Physical shared files and sealed164 objects are explicitly reused rather
  than claimed as newly read Source originals.
- 384 path observations yield 116 content-and-extent bundles. Adoption of the
  preceding20 assets adds2 otherwise absent bundles:118 expanded bundles in total.
- 17,126 original unique contents total186,957,779,446 bytes before the2 additional
  prior contents. After20 prior assets and a separately committed SRAD bundle are
  reused, planned new expanded transfer is144,784,555,300 bytes in30 batches.
- These are asset counts, not EP-qualified scientific workloads or certified
  full-capture counts. Explicit fraction paths and unconfirmed extent stay distinct.

Four BICG/ATAX Source files were retired by a different explicitly authorized
storage task. Their exact frozen identities, prior full-SHA proofs, retirement
receipts and current164 identities match. EP-MAIN independently reopened and
hashed all476,562,384 bytes on164. No removed Source file is claimed as newly read;
none of those deletions or space savings is attributed to this task.

The same task verified and retired the original17,943,970,556-byte polybench.tgz.
Its true164 copy has SHA256
`9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`.
The archive inventory reads that object and retains the original Source provenance.

## Dedicated bounded channel

The other storage task owns the original Source sender/Target receiver leases.
EP-MAIN does not stop it, remove its locks, or take over its destination. Instead,
the user-authorized parallel task uses exclusive leases
`.SHARED_SM70_LIBRARY_SOURCE.lock` and `.SHARED_SM70_LIBRARY_TARGET.lock` in the
existing bridge. All payloads remain under this task's unique immutable164 paths.
These zero-byte lease files are control metadata, not staging payload.

Pinned original copy engine SHA256 remains
`f4269a5c8f9505754545a40324f28853aa9eaf29d452df4674309bc697ee6159`.
The reviewed derived engine is
`c937d48e3c2ffbcb84d15fa065af89f4b2c119cc554747f3c4749c53051cf261`.
The V9 atomic no-replace primitives remain pinned and unchanged. Each channel has
one writer; this does not assert that all independent projects share a single
15MiB/s aggregate limit.

The channel retains128MiB frames, a15MiB/s transfer maximum, exact Source identity,
whole-file SHA/EOF, close/reopen SHA, committed range coverage and COMMIT-last.
IO PSI adapts physical reads to30/10/4/1MiB/s. The native floor is5GiB plus every
registered write reservation,1GiB other-project headroom and64MiB task controls.
Other scientific controllers and their policies are unchanged.

Synthetic revision ISOLATED_V6 passed interruption/range reuse, idempotence,
archive ordering, full close/reopen SHA, path traversal rejection and independent
complete native restore. The separate native backend fixture also passed.

## Whole archive coverage

The revised reader scans beyond tar zero terminators, including concatenated tar
and gzip members. It rejects nonzero malformed/truncated tar headers, validates
gzip CRC and decompressed EOF, and checks whole physical archive SHA and identity.
Previously computed member SHA values can be reused only when the new complete
archive SHA and each member's exact ordinal/name/metadata match. Inflated bytes
are not charged twice as physical IO.

Both the inventory and the actual payload sender passed concatenated tar/gzip
positive fixtures and bad CRC, truncated gzip, invalid header negative fixtures.
Inventory cache reuse and different-archive-SHA rejection also passed. Four real
archive inventories are being rerun/continued under these stronger conditions.

## RTX4080 and semantic scope

The frozen v7 ordinary-domain producer and its constant-memory consumer have
real GPU and native epoch2 evidence. The non-perfect constant test actually
issued27 L1C accesses (18 misses,9 hits) and11 constant transactions. This is
engineering semantic compatibility, not hardware performance qualification.

The CALL v8 candidate decoded its instructions but issued zero instructions in
its first exact native case. That case remains a failure, consumes its one fresh
budget, and is not reported as PASS. Its64-bit PC issue is being repaired in a
separate candidate. Specialized control-flow/API/instruction domains remain
explicitly held until their own measured evidence passes.

The shared library is not yet declared complete. Expanded transfers, archive
findings, public cross-project access and all-object independent bounded native
restore must finish. Bulk4080 coverage also requires a closed exact version/input
denominator, accepted captures or explicit supported exceptions, and164 readback.

## Additional independent closeout

The parent independently rehashed both Ada stage1 engineering archives and all351
manifest members on true164. Only the two terminal requests had their128MiB
write reservations reduced to zero through the existing epoch2 exclusive lock
and registry/epoch pointer update. Consumed attempts, exact budgets, global
remaining budget and all foreign records are unchanged. The failed CALL request
retains its separate reservation. No native hot outputs were removed.

Six completed audit/hash ledgers (56,447,059 bytes) were fully written to164,
closed, reopened and independently SHA-verified before their native paths became
symlinks to the immutable cold objects. This frees native control allocation
while preserving existing reader paths. It is separate from retirement of
original Source workload assets.
