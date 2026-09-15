# C12--C15 old174 source archaeology V1

Status: `PARTIAL_COMPLETED_AUTH_BLOCKED`.

This is the final inventory/review round for historical C12--C15 TLB/Cache
simulation assets.  It is an archaeology record, not a new experiment and
does not rerun a simulator or a GPU workload.

The expected coordination input is
`103641562b6474e22192c19d1bd81dd12d88ce61`.  The live old174 endpoint
`root@10.208.130.174:2233` accepted a TCP/SSH handshake on 2026-09-15, but
rejected the available key identities with `Permission denied
(publickey,password)`.  Consequently, this package does not assert that an
old-container-private file exists, was deleted, or is duplicated on old174.
Every such reference is deliberately `MISSING_OR_UNKNOWN` pending a
credentialed read-only inspection.

Local mount inspection proves that this container's `/root/share` is a rw
ext4 mount from `/dev/md127` and `/root/data` is a rw ext4 mount from
`/dev/sdf[/huangrulin]`; `/workspace` and `/tmp` are this container's overlay.
The shared-mount migration manifest records a 2026-09-06 rsync relocation of
several historical `/workspace` trees into `/root/share`.  That is strong
local relocation evidence, but not proof of visibility inside old174.

Classification is exhaustive and exclusive at the asset row level:
`SHARED_VISIBLE_UNCHANGED`, `OLD_DOCKER_PRIVATE_MUST_MIGRATE`,
`GIT_AUTHORITY_ONLY`, `REDUNDANT_ARCHIVAL_COPY`, or `MISSING_OR_UNKNOWN`.
No row is `OLD_DOCKER_PRIVATE_MUST_MIGRATE`: old-private existence could not
be proven under the authentication boundary.

`SHA256SUMS` is generated after all review-pack contents are final and covers
every pack file except itself.  `CODEX_REPORT_SHA256` separately closes the
Codex report named there.  The report records the same evidence boundary.
