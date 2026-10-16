# PolyBench restoration evidence after all 35 range closeouts

The existing receiver remains the only data pipeline. Do not run this phase while
any bridge batch has payloads, or while Lane1 holds a legal compilation lease.
No additional transfer service or process watcher is required.

1. Require all 35 frozen V2 range receipts, target GitHub publications, independent
   source SOURCE_KEEP acknowledgments and exact bridge closeouts. Their ordered
   offsets must cover precisely 17,943,970,556 bytes without gaps or overlap.
2. Invoke the already deployed `polybench_range_receiver.py --finalize`, using
   the existing pinned COPY_SCOPE publication and V2 plan. It reopens the owned
   destination, hashes the entire archive, and only then renames the owned partial
   to the canonical absent destination. Expected whole SHA256:
   `9feffb121c304412ea7b8289e9ae0c7cabff5aef2098ff025fb65af2f43653ca`.
   Publish and remotely read back the resulting whole-archive receipt.
3. Independently read the completed 164 archive as a streaming gzip/tar. Reuse
   the source's exact stage-to-member mapping: remove the first component of each
   nonempty frozen stage relative path, retaining `polybench/...`. Match all
   eleven regular members, their exact sizes and SHA256 against frozen manifest
   `bca6dfc2b43f4715ce0c6e55d4faa8ae11f3f4c7be7b96279e5671489004f274`.
   Total selected uncompressed content is 66,331,215,249 bytes. Reject duplicates,
   missing selected members, nonregular selected entries and hash discrepancies.
   Verify gzip completion; do not materialize the 66GB stage on old174.
4. Reopen the two separately preserved zero-byte completion markers and verify
   the empty-file SHA256. Match all 13 file and 14 directory metadata entries to
   the pinned numeric UID/GID/mode/nanosecond sidecars. SSHFS attributes are a
   projection, not proof of original native permissions. Keep this distinction
   explicit in the restoration receipt.
5. Coordinate any independent bounded reverse validation with old174 through the
   same unique bridge window, only after forward payloads have all closed. Each
   physical batch stays <=512MiB, <=30MiB/s and above the 40GiB Share floor.
   Old174 owns any no-overwrite native import and native metadata verification.
   Target streaming member recovery does not claim a full native 66GB restore.

An eventual native restore uses a fresh, absent destination and the exact frozen
member mapping; it does not extract over an original stage. Apply original numeric
metadata from the immutable sidecars on a native filesystem, then independently
verify every restored path/hash and directory entry before any release review.

Whole archive verification and streaming restoration do not authorize deletion.
The original compressed archive and both original closeout stages remain
SOURCE_KEEP throughout this night. Record primary archive bytes, independently
recovered member bytes and actual old174 source release separately. R10 source
release for PolyBench remains zero.
