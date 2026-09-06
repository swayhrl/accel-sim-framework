# M5.0BT — 2MM local storage-admission stop

Status: **REMOTE_ARCHIVE_PASS; ARCHIVE_ONLY_COPYBACK_IN_PROGRESS;
STOP_LOCAL_STORAGE_ADMISSION; NO_RECAPTURE**.

This is a fail-closed transfer receipt, not a capture or trace-fidelity
failure.  It records the exact 2MM transfer boundary so that resumption can
copy the existing immutable remote archive after destination capacity is made
available.  No GPU application, trace capture, archive, remote bundle, or
locally verified scientific payload was deleted, restarted, or replaced.

| item | observed value |
| --- | ---: |
| remote state | `ARCHIVE_PASS` |
| remote archive bytes | 3,416,630,277 |
| remote complete bundle bytes | 50,301,968,376 |
| remote archive SHA-256 | `59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e` |
| immutable-receipt safety margin | 4,294,967,296 |
| exact local required bytes | 58,013,565,949 |
| local free bytes at gate | 36,313,600,000 |
| shortfall | 21,699,965,949 |

The wait-only copyback controller reached `ARCHIVE_PASS`, calculated the
unmodified receipt requirement
`archive + complete_bundle + 4 GiB`, and exited with its documented
`STOP_LOCAL_STORAGE_ADMISSION` result before opening `rsync`.  Consequently
the original receipt path produced no unpacked 2MM bundle, no
`COPYBACK_SHA_PASS`, and no `LOCAL_IMMUTABLE_PASS` claim.

After that fail-closed stop, researcher authorization started one separate
`archive-only` rsync of the exact already-created `.tar.zst` to the same
SIM_HOST namespace.  It intentionally does **not** unpack, run internal
bundle validation, rewrite `kernelslist.g`, or promote any trace/formal
result.  During this transfer the local archive is necessarily partial and
must never be treated as a receipt.  Its sole purpose is to preserve a
compressed local copy while capacity recovery is investigated.  Completion of
the archive-only copy does not change the remaining hard receipt requirement.

The current SIM_HOST filesystem and its accessible alternate mount have no
sufficient free capacity.  Existing local immutable scientific bundles are
preserved.  The required source-correct recovery is to provide at least the
recorded destination capacity, re-run the **transfer-only** receipt path
against this exact remote archive SHA, then require archive SHA, internal
`SHA256SUMS`, controller `valid_bundle()`, and immutable receipt validation in
that order.  It is forbidden to recapture 2MM merely because this transfer
admission stopped.

This evidence leaves M5.0BT ACTIVE.  It does not change formal configuration,
payload identity, result registry, capture priority, or any running SIM_HOST
replay.
