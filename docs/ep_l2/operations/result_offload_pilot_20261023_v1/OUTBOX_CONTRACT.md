# Independent result outbox: a data export contract, not a scheduler

Outbox entries are immutable **references** to owner-frozen completed files, not copies/hardlinks into an active result directory. Never chmod/chown/rename/hardlink/reflink scientific originals or append a storage field into scientific registry. No polling daemon or automatic discovery of arbitrary raw files. Source owner explicitly publishes a bounded COPY_READY; a finite foreground Lane T invocation consumes one exact descriptor, then exits/HOLDs. Pending entries are capped; no second sender/receiver.

Proposed isolated control layout: `<approved-control-root>/<project>/<campaign>/<attempt_uuid>/<descriptor_sha>/` containing SOURCE_EXPORT.json, immutable SOURCE_MANIFEST shards and directory records, manifest hashes, PATH_MAP, per-range receipts, ARCHIVE receipt, RESTORE receipt and SOURCE_KEEP ACK. Large scientific sidecars remain payload referenced by full SHA, not duplicated inline. Directory records and schema/selector/native target root bind the whole manifest hash. New result transactions never reuse P9/industrial txids or selector skip lists.

Four independent axes must be present:

| Axis | Authority and valid meanings | Cannot imply |
|---|---|---|
| science | Original E/E2 or BA receipt: NOT_EVALUATED / ACCEPTED / REJECTED / HOLD | Archive success cannot change it. A failed diagnostic may stay REJECTED after a perfect archive. |
| archive | Target: NOT_STARTED / PARTIAL / ARCHIVE_VERIFIED / HOLD; exact raw+compressed hashes, full range coverage, manifest and COMMIT | Not native restore, science correctness or freed bytes. |
| restore | Independent verifier: NOT_TESTED / RESTORE_VERIFIED / HOLD, explicit file count and native filesystem/location/metadata scope | A sample is not whole-selector restore; Target-native is not native164. |
| local_reclaim | Source owner: SOURCE_KEEP for every entry in this pilot | No deletion eligibility or execution is implemented. Future proposals need separate explicit approval and reader closure. |

An accepted science record may legally have archive PARTIAL and restore NOT_TESTED. It remains scientifically accepted and SOURCE_KEEP, with storage failure reported separately. A partially archived failed result remains failed. No receipt changes Source budget or controller admission. Scientific completion order and accounting remain exclusively the projects' existing responsibility.

V9 canonical txid stays bound to filesystem identity/root, selector SHA, source frozen commit and genuine164 destination. New outbox adds a canonical descriptor SHA binding project/campaign/attempt UUID, exact science receipt hash and lifecycle owner statement. Every range receipt and final archive/restore/ACK joins **both** identities, so a reused payload identity cannot be misattributed across projects. Source commit is execution/provenance commit, not whichever publication branch currently happens to be HEAD. Whole manifest SHA binds directory/sidecar policy separately.

Pipeline: explicit owner freeze -> exact COPY_READY+resource identity -> finite sole-receiver admission -> bounded chunk -> durable close/reopen SHA -> immutable range receipt -> verified duplicate reuse on restart -> full ordered original SHA and manifest coverage -> no-overwrite COMMIT -> ARCHIVE_VERIFIED -> fresh ABSENT native restore -> full raw SHA and numeric file/directory metadata -> RESTORE_VERIFIED -> persist164+Git proof/readback -> Source independent SOURCE_KEEP ACK. Existing bridge-payload cleanup rules remain scoped; this phase cleans nothing and a future fixture may only reconcile its explicitly owned newly created temporary paths.

No metadata-only synthetic payload may be presented as a complete real result. Empty files/directories are explicit members; symlinks/hardlinks are rejected until an approved selector-specific policy exists. A missing164 mount, wrong root, stale/mismatched receipt, changed byte identity, unclosed writer, cap breach or incompatible protocol is HOLD. Complete orphan adoption is narrow and hash-bound; partial/corrupt content is retained for inspection, never auto-truncated. An existing final destination with any different byte fails without replacement.

Fsync/close/reopen and the existing164 protocol are the initial evidence scope. Do not relabel them as a new server-native power-loss guarantee. The future synthetic/native restore location is the new Target scratch on local ext4, explicitly separate from persistent164 archive. No native164 login or TLS tmpfs reuse is required for that labeled test scope.
