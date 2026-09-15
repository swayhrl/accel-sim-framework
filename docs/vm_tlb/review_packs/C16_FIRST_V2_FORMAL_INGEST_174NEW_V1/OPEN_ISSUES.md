# Scope boundary

- Both containers independently pass; all active addresses fall outside the hash-bound object ranges, so `UNKNOWN_RUNTIME` is preserved rather than fabricated.
- C16WARP1/static-map data record load/store but no byte width; width is explicitly `UNKNOWN_NOT_REPRESENTED`.
- Aggregates are set-based only: cross-MREF order, reuse distance, and global hardware order are unsupported.
