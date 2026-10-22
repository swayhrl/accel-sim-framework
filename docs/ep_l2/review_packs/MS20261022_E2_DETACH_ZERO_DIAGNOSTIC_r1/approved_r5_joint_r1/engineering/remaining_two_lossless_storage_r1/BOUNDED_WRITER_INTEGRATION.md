# Ready candidate: root deployment and exact writer calls

This directory is frozen candidate source only. No actual source/registry/CLIENT
or application has been changed. 19 tmp-only controls passed, including two real
commits/pushes/own-commit fetches to a temporary local bare Git repository.

Deploy `bounded_metadata_writer.py` + `tagpressure_physical96.py` through original
STOPPED/no-active-E-lease source publication/CLIENT activation. Seal policy only
after actual BEGIN journals and independent root writer-adoption review. Default
POLICY_REF=None retains160MiB. Use sharing author's final metadata base plus only
our import/call delta; do not overwrite sharing credit changes with this old-base
complete metadata file. Generation160/condition and640/batch remain untouched.

For EACH Vector/Conv, before its first mode96 forecast:

1. Instantiate Writer(root=OUTPUT/E2_R5_BOUNDED_METADATA_PHYSICAL96_ACCOUNTING_r1/
   exactcid, condition_id=exactcid, repo=actual E, allowed_roots=explicit root-owned
   metadata destinations, create=True). Original OUTPUT genuinely counts this
   journal/body store. Begin doesn't create a controller or lease.
2. `activation_candidate()` returns actual header SHA + actual Writer source ref.
   Root verifies it, sets root_actual_activation_reviewed=True, then writes the
   activation JSON through `writer.write_json` and publishes/adopts signedpolicy
   with both exact activations. Do not manufacture activation files before BEGIN.
3. Policy carries exact source/finalmanifest, original paid57 attempt-prefix SHA,
   target conditions,96physical/160generation/640batch, actual writer source ref,
   root signature, independent review, and bounded_writer_rules_actually_adopted.
   Only then bind tagpressure_physical96.POLICY_REF to exact real policy ref.
   Helper reads actual journal under SH lock before returning96; DWT/CFD stay160.

Actual postprocessing:

- Existing full independent CLI still has64MiB prewrite cap; compact has8MiB.
  Run each once into its fresh /tmp output. `writer.import_existing(path,'review')`
  /`'compact'` hardlinks the original inode to OUTPUT body store; never copy raw,
  run_status or terminal_summary. These fresh one-off files become immutable.
- Every root-created point/report/status/D-event/readback/control/receipt version
  must use `writer.write_json`, `write_bytes` or `copy` BEFORE filesystem mutation.
  `copy` is content-preserving immutable hardlink alias/atomic rename, never
  truncation of prior evidence inodes. All complete versions/journal growth are
  budgeted: review64,compact8,othercontrols2MiB, <=63 distinct bodies plus journal.
- Root code must replace old shutil.copyfile / write_text / JSON direct writes for
  these new condition metadata destinations. It must not claim mode adoption if
  those routes remain unbounded. Other existing project resources are untouched.
- For legacy fixed helper snapshots, register every exact source body first;
  call `before_alias(exact ownerstore/SHA.suffix,sha)` and
  `before_alias(exact OUTPUT-accounting/SHA.suffix,sha)` BEFORE that fixed helper
  creates a version/copy/link. Its one immutable body copy+hardlink per SHA/suffix
  is the only permitted non-Writer body-copy route; no repeated arbitrary
  shutil copies. Existing already-accounted body may be reused. Register/control
  all generated helper request/snapshot/close/readback JSON through Writer.
- Before any publication, `writer.publication_check(full inventory)` requires
  all complete new body versions+journal<=12MiB. Otherwise metadata-publication
  HOLD; leave terminal/raw/current central result intact, no truncation/retry.
  Initial64+8+2 retention remains safe within96; a huge complete report need not
  be publishable. Never mark missing-evidence points accepted.

Exactly TWO publication attempts/condition, failures consume attempts BEFORE Git:

1. First `writer.publish` publishes acceptedpoint+fullreview+compact+REPORT and
   exact small supporting metadata. All registered requested paths, including
   unchanged paths, appear in actual remote verified inventory.
2. Before creating unpublished top-level D receipt, use first real complete
   readback for metadata snapshot/closure driver. Emit D reference to commit1;
   write/record subsequent closure/status/event/receipt metadata via Writer;
   second `writer.publish` commits these together. Save/account second readback
   locally; no third publication. Next condition's first publication may include
   prior small readback ONLY after registering it as currentcontrol too.

`publish` owns the ORIGINAL E_GIT_PUBLICATION.lock: do not nest another flock on
that same lock. Uses per-process no autoGC/maintenance/commitGraph/submodule
recursion. REQUIRED executable hooks or signing/filter transformations cause
HOLD and are never bypassed. Fetch only the already-local own exactcommit,
verify actual advertised branch, then byte-read back every requested path.

96MiB proof: all distinct bodies<=12MiB, <=6 conservative full-body physical
copies including ordinary/fixed helper/Git/transient copies =>72MiB. Extra24:
index/index.lock8 (two attempts, each actual+futureindex<=2MiB), cumulative trees/
commit5 (eachattempt rawtrees<=2MiB, cumulative<=4MiB and<=128 treeobjects), file/
dir rounding7 (<=64 newdirs, <=64bodyversions,<=6 bounded aliases), ref/reflog/
header/control overhead4. Writer enforces alias slots and dirs BEFORE copy/mkdir;
full exact pipeline routing is mandatory, not an assertion after writing.

Original resource_guard, endpoint384MiB, newobserver64MiB,5GiB floor+2GiB monitor,
all historical counts/results,10/24 generation and formal source/Q/input remain.
