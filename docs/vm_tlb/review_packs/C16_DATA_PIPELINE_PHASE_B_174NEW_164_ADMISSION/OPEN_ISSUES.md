# Phase B open issues

There are no data-root blockers from this admission canary.

1. Phase C remains review-gated. It must begin with synthetic fixtures only;
   Phase B does not authorize scientific transfers.
2. The root is SSHFS (`fuse.sshfs`), not local ext4. Phase C must retain
   immutable `RUN_ID`s, write-then-fsync-then-reopen-and-hash, no-overwrite
   `renameat2(RENAME_NOREPLACE)` behavior, immutable catalog entries, and
   destination verification before an ACK. These are protocol requirements,
   not a Phase B limitation: all listed primitives were observed supported.
3. No R5 or RTX3090 raw/import manifest has been admitted. Their authority and
   import timing remain unchanged.
4. The root mode is `0777`, owned by remote UID/GID `1011:1011`. This was
   observed rather than altered. Future access-control changes need a separate
   storage-administration decision and must not be bundled with scientific
   transfer work.
