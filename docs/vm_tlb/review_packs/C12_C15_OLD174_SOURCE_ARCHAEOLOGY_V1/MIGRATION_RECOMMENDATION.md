# Migration recommendation

1. Retain all `SHARED_VISIBLE_UNCHANGED` assets in their existing shared paths.
   Their local mount and representative hashes are recorded in
   `SHARED_PATH_PROBES.tsv`; no copy is authorized or needed in this round.
2. Treat Git paths/commits as authority for scripts, configuration, trace
   manifests, and derived review packs.  Do not export Git source trees as
   archival raw data.
3. Before old174 Docker retirement, obtain read-only authentication and run a
   narrow inventory of the five `MISSING_OR_UNKNOWN` private scopes.  For each
   proved scientific private-only asset, record path, size, file count,
   SHA-256, trace/config/run lineage, then copy (never move) to an agreed
   shared destination and independently hash-verify.  Only then classify it
   `OLD_DOCKER_PRIVATE_MUST_MIGRATE`.
4. Preserve `C12_FINALIZER_STATE.json` as a `REDUNDANT_ARCHIVAL_COPY` with its
   stale state marking.  It must not override the later terminal matrix.

No bulk migration is recommended while the authentication boundary remains.
