# V6 target: S01 DEST_VERIFIED, waiting independent source action

The existing V5 handshake and sole target window continue. No Goal, nonce, source copier or historical pack backup was restarted. V6 837ca9e1a6cf520f14a381416ef65f9b05cc3f83 was read in full.

S01: 52 files / 418020580 B copied by one exact files-from rsync at 30MiB/s after a read-only dry-run and complete bridge SHA256 checks. All SSHFS files were closed/reopened and match source/bridge SHA256; immutable DEST_VERIFIED was published to the authorized archive root and compliant bridge. Source READY SHA256: 0b3fa5be7f5000f39349bd4b43e85a353fb9c58fe4ba1a5631c2fac162111751. Frozen 102-file inventory SHA256 remains d34a952f7dfa5fcd0a2a965fc82623a6ff5fb9666f007b7626269e295a8505d7.

One 8234735 B archived file was restored into an independent path beneath the authorized archive root and fully hashed. This is a sampled restore, not whole-batch RESTORE_VERIFIED. Target verification level is SSHFS_READBACK_VERIFIED, never native-server verification.

Source release is exclusively the old174 source Ops responsibility. No source release receipt is consumed yet: confirmed released allocated bytes 0; actual source df change unknown. Source files remain SOURCE_KEEP pending the independent source recheck/action. Bridge data is retained until the source action handshake closes. S02 follows that handshake; no second rsync is launched.

Minimal receiver in tools/archive_receiver.py defaults to read-only planning, requires explicit --receive plus exact READY SHA, checks roots/path traversal/symlinks/frozen membership/stability/512MiB/Share>=40GiB, uses a single kernel target lock and one sequential rsync, rejects existing archive files, and has no source deletion operation. General cold project acceptance requires explicit owner COLD_COPY_OK and SOURCE_KEEP retention; project names do not confer permissions. Multi-project index and recovery workflow are being completed alongside the current migration.

All 36 legacy pack archives are retained without recopy; their old route remains recorded as noncompliant with V4, and original packs remain SOURCE_KEEP. No six-lane or DTC-L1 task/runner/registry was modified. Neither archive bytes nor sampled restore bytes count as recovered source space. All existing admission gates remain unchanged.
