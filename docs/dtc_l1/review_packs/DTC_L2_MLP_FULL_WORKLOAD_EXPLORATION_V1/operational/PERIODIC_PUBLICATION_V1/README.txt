Periodic publication V1: qualified engineering candidate, not started by B

Main owns configuration, source publication and process start. No model,
simulator controller, consumer, registration or budget operation is performed.
The source reads live JSON and the SHA-pinned D generator; it never imports
live l2_results.summary or writes experiment AUTO_SUMMARY. All generated large
outputs, logs and controls are on164, independent of the live experiment root.

Configuration: CONFIG.template.json. Main must replace expected_initial_head
with W HEAD after publishing the source. Configuration accepts only public
paths, pin and interval fields; each snapshot contains PUBLISHER_CONFIG.json.
No token/credential is stored in configuration. GIT_TERMINAL_PROMPT=0 is set.

Main foreground first cycle:
PYTHONDONTWRITEBYTECODE=1 python3 periodic_publisher.py --config CONFIG.json --once

Main background loop:
PYTHONDONTWRITEBYTECODE=1 nohup python3 periodic_publisher.py --config CONFIG.json >> /164/output_root/publisher.log 2>&1 < /dev/null &

Use the actual absolute source/config/output paths. The loop runs immediately,
then every1800 seconds after a successful publication, sleeping only30 seconds
between checks. No background process is started merely by importing this file.
Create output_root/control/STOP to stop naturally after the current bounded
transaction. PID.json and STATE.json are atomic; the process flock rejects a
duplicate publisher. All Main manual Git transactions must use the same
archive_root/coordinator/git.lock. This lock covers generation, staging,
commit, push, ls-remote and HTTPS readback.

Each snapshot exports all primary cycles, states, coverage and figures using
the existing D report's accepted predicate. Source RESULT SHA/UUID/cycles are
checked before/after generation and against previously published identities;
changed or disappeared prior results HOLD, never replace. The first export
contains all accepted primary structured documents; later exports contain
only newly accepted identities. original_utf8.encode('utf-8') reconstructs
the exact original RESULT bytes and source SHA. Supplemental trials (R2) are
read separately from authorized_supplemental_trials and never unioned with
the primary matrix or substituted for the original negative. Snapshot-local
.gitignore unignores only*.jsonl.gz, including under a global*.gz rule.

Main-approved analysis READY schema:
{"schema":"MAIN_APPROVED_ANALYSIS_PUBLICATION_V1",
 "status":"MAIN_APPROVED_FOR_PUBLICATION",
 "files":[{"path":"/164/absolute/file","sha256":"exact SHA","name":"file.md"}]}
Missing READY publishes base data. Existing invalid or changed READY HOLDs;
no analysis is invented or automatically approved. File names are basenames.

Root README current links are updated; its original full text stays in a
historical details block. Historical root/checkpoint manifests stay unchanged;
each new snapshot has its own MEMBER_MANIFEST. The README explains partial
coverage, missing CH controls, per-file rather than global transaction scope,
old BATCH_STATE .88 labels and unchanged English v0.23.

Only explicit snapshot files, root README and PERIODIC_CURRENT.json are staged.
Unrelated tracked/staged changes HOLD; unrelated untracked files and pycache
are left untouched. Git commands are bounded. A failed push/readback retries
the same durable pending commit instead of producing another snapshot/commit.
No force/reset/rebase or source-result edit is used. Success requires matching
remote branch ls-remote plus HTTPS SHA readback of root README/report/manifest.

Recovery limit: a crash during copying, before COMMITTING STATE is durable,
can leave owned worktree files and cause a clean-guard HOLD. Main must inspect
those files; the publisher intentionally does not reset an uncertain tree.
Once COMMITTING is durable, exact base/message/file hashes recover only its
own single commit. Unexpected HEAD or staged changes HOLD for Main review.
Failures affect publication only and never interrupt healthy simulations.

CPU_QUALIFICATION uses an isolated local repository/bare remote, fixture-only
HTTPS byte replies and dummy JSON. It tests delta/no replacement/no union,
original byte recovery, duplicate lock, dirty/staged guard, inherited gzip
ignore, exact pending-commit retry, lock held across push and unrelated-file
preservation. No live generator, GitHub push or background launch occurred.
