# Shared Git object-store relocation — 2026-09-22

## Status

`PASS` — the shared `accel-sim-framework` Git object store was relocated from
the constrained overlay filesystem to the dedicated `/root/share` ext4
filesystem.  This is repository-storage infrastructure only; it does not
alter simulator code, configurations, traces, scientific inputs, accepted
evidence, or any Wave-A result.

## Scope and rationale

All registered `accel-sim-framework` worktrees use the common Git directory
`/workspace/repos/accel-sim-framework/.git`.  Git writes temporary pack files
next to the common object store, so setting a generic temporary-directory
variable would not redirect these writes.  On 2026-09-22, the overlay
filesystem had only about 6.8 GiB free and contained 139 stale
`objects/pack/tmp_pack_*` files totaling 46,888,300,841 bytes (43.67 GiB).
They were confirmed not to be active Git packs, removed in the preceding
storage-recovery action, and followed by a successful connectivity check.

The permanent, common object-store path is now:

```
/workspace/repos/accel-sim-framework/.git/objects
  -> /root/share/accel-sim-framework-object-store/objects
```

The first path is a symbolic link.  The target resides on `/root/share`, an
independent ext4 filesystem.  No per-command `GIT_OBJECT_DIRECTORY` or
`GIT_ALTERNATE_OBJECT_DIRECTORIES` override is used; this is essential so all
worktrees and all normal Git invocations share one coherent writable object
database.

## Preconditions

The operation began from master coordination commit
`2c5e5d229f84574bb92c42884c5f5b87897cf8e8`
(`hrl/iscas2027-dtc-granularity-fairness-v0`).  The following were required
before the switch:

- no running Git writer/maintenance process and no Git lock or `gc.log`;
- a successful `git fsck --connectivity-only --no-dangling`;
- an absent destination and absent source-side backup path;
- no simulator, trace, GPU job, or scientific workflow launched or changed.

One unrelated `git add` observed during the initial survey was allowed to end
naturally; no action was taken until the later quiescence check passed.

## Executed migration and evidence

1. Created the private destination root
   `/root/share/accel-sim-framework-object-store`.
2. Generated sorted, relative-path SHA-256 manifests for every regular source
   object file and recorded the file-count/byte-count summary.
3. Copied the complete `objects` directory with preserved attributes to the
   destination; generated the corresponding destination manifest.
4. Compared both manifests and summaries.  Both were exactly:

   ```text
   files=3188 bytes=233605720
   ```

5. Repeated the no-writer/no-lock check.  Renamed the source object directory
   to a same-filesystem temporary backup, then created the source-path
   symbolic link to the verified destination.
6. Verified that resolving the standard common object path yields exactly
   `/root/share/accel-sim-framework-object-store/objects`.
7. Ran `git fsck --connectivity-only --no-dangling` again.  It passed.
8. Verified `HEAD^{commit}` resolution and `git status --porcelain` reads for
   the primary worktree, the Wave-A master, and the SG0, SG1, SG3, SG4A, and
   SG5 worktrees.  All passed.
9. Deleted only the verified source-side backup after those checks passed.

## Postcondition and operating rule

Immediately after the migration, the overlay had about 52 GiB available and
`/root/share` about 126 GiB available.  Future Git temporary packs and normal
object writes therefore use the `/root/share` target.  Before pack-intensive
Git maintenance, fetch, or push work, check free space on both filesystems;
the target filesystem remains highly utilized and is not an unlimited scratch
area.

This document is the only repository-content change made by the relocation.
The commit containing it is also the post-migration write/push verification.
