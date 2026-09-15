# C12--C15 old174 source archaeology report

Status: `C12_C15_OLD174_SOURCE_ARCHAEOLOGY_PARTIAL_COMPLETED_AUTH_BLOCKED`.

The review pack is
`docs/vm_tlb/review_packs/C12_C15_OLD174_SOURCE_ARCHAEOLOGY_V1/` and is
anchored to coordination commit
`103641562b6474e22192c19d1bd81dd12d88ce61`.

## Outcome

The local filesystem truth is reconstructed to the supported boundary:

- `/root/share` is locally a rw `/dev/md127` ext4 host-backed mount and
  `/root/data` is locally a rw `/dev/sdf[/huangrulin]` ext4 host-backed mount.
  The migration receipt (`d7c183bf0f96ff78dc9046b7f5ef6395981b444e03c433c9c8152d9c82f1f1a2`)
  records an rsync-verified relocation of relevant historical `/workspace`
  trees into `/root/share`.
- Shared retained assets include the M4A archive-source tree (10,166,713,715
  bytes, 4,695 files), M4C controls (582,305,043 bytes, 14 files), M4BS replay
  logs (557,253,823 bytes, 18 files), and M4I staging (199,798,756 bytes,
  1,512 files).  Representative semantic manifests close at
  `ee53ca249cd45e2fd4da6920db4038673636960d6f36f2f99789062412636908`
  (prefill) and
  `9bb152d8475f7827e58071a7f765b2b00c5a2d08161a306f9031ff00a8f48701`
  (decode1).
- C12 raw-log identities, trace/config/binary/core provenance, C13 repaired
  exact-mode receipts, C14 microdiagnostic receipts, and C15 static boundary
  records are recovered through their immutable Git authorities.

## Classification and scientific boundary

`SHARED_VISIBLE_UNCHANGED` is used only for locally observed shared-mount
assets.  `GIT_AUTHORITY_ONLY` is used for source/config/manifest/derived
records where Git is the authority.  The stale C12 finalizer state is retained
as `REDUNDANT_ARCHIVAL_COPY` with `OBSOLETE` status.  No asset is asserted as
`OLD_DOCKER_PRIVATE_MUST_MIGRATE`, because its old-private existence has not
been established.

The scientific labels are intentionally conservative: C12 F0 remains the
prior formal baseline record; C12 candidate arms, C13 repaired comparisons,
C14 microdiagnostics, and C15 static material are diagnostic; uninspectable
old-private paths are unknown.  C14 is explicitly not full-ROI equivalent and
C15 contains no new native capture or dynamic simulator evidence.

## Blocker and next action

The old174 endpoint `root@10.208.130.174:2233` is reachable but rejected the
available SSH public keys (`Permission denied (publickey,password)`).  This
prevented the required read-only inspection of old Docker-private `/workspace`,
other `/root` paths, `/tmp`, and overlay storage.  With an authorized
read-only credential, inventory those paths narrowly, hash-close any proved
private scientific asset, and only then make a copy-based migration decision.

No simulations, GPU workloads, migrations, deletes, cleanups, or ChatGPT
handoff changes were made.
