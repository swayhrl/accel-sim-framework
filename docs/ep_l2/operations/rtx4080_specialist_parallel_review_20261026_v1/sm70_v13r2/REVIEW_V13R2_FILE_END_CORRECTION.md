# V13R2 exact FILE_END evidence wording correction
Private, unlaunched candidate; V13 files and its final manifest are preserved.

For only _qualified_fuse_alias_context archive frames:
- source_before_after_identity_unchanged = null, so complete identity equality is not claimed.
- stable_fields_excluding_FUSE_inode = true.
- policy = EXACT_ROOT_FUSE_ALIAS_PLUS_ARCHIVE_AND_MEMBER_SHA.
- whole_archive_proof = PENDING_UNTIL_SOURCE_DONE. FILE_END proves the selected member's full SHA; it does not prove entire archive closure. Existing complete archive physical EOF and whole SHA gates still run before SOURCE_DONE.

General source_send is AST-identical, and a nonalias archive FILE_END is byte-semantically unchanged. The receiver migrate function is AST-identical to V13: it uses member path/size/SHA and does not depend on the old boolean or newly added policy fields.
63 V13 CPU tests were rerun against V13R2 and passed. Nine additional real small-gzip/tar sender frame checks passed: alias/nonalias FILE_END, SOURCE_DONE after actual synthetic member/archive hashes, unchanged receiver and general-source/audit helpers. The real framed fixture archive is147 bytes; no production source/body or range hashing was started.

Fresh exact V13R2 Root approval remains mandatory. No ROOT_APPROVAL.json exists and no supervisor/driver/sender was started. Engine, driver and supervisor pins have been updated consistently.
