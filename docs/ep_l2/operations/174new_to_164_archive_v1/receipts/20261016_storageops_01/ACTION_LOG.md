# Action log

All audit commands below executed in the 174-new SSH container. No secret/key material or complete SSH configuration is included.

## Setup and preliminary probes

- GitHub connector fetched the complete frozen GOAL.md successfully; local independent fetch/read confirmed SHA 543a88d63f899ccfa4f6c569245496d6deb8fdf2.
- Inspected SSH namespace identity, selected path metadata and workspace OWNER.md; no permission changes.
- An initial nested shell-quoted SSH probe failed authentication; trailing read-only metadata commands ran in the local 174 namespace. Those trailing results were discarded as remote evidence. The argument-array subprocess probe below corrected this transport issue and also failed authentication (255).
- Source-container git ls-remote timed out after 45 seconds; publishing was moved to the independent Windows checkout, where git ls-remote and shallow filtered fetch succeeded (0). No source-container branch/ref or worktree was created.
- Local setup executed git init, remote add, gc.auto=0 fetch --filter=blob:none --depth=1 --no-tags, sparse-checkout, and switch to the requested independent execution branch; all returned 0.
- Full Goal read from fetched commit and applicable instruction-file checks completed. No subagents were launched.

## Reproducible read-only audit

`Get-Content audit_readonly.py -Raw | ssh -o BatchMode=yes -o StrictHostKeyChecking=yes hrl-174-new "python3 -"` returned 0. Output is AUDIT_EVIDENCE.json.

1. Executed `df -B1 -P /tmp`; exit=0; timed_out=False.
2. Executed `findmnt -T /tmp -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
3. Executed `df -B1 -P /root/workspace`; exit=0; timed_out=False.
4. Executed `findmnt -T /root/workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
5. Executed `df -B1 -P /root/workspace/accel-sim-framework`; exit=0; timed_out=False.
6. Executed `findmnt -T /root/workspace/accel-sim-framework -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
7. Executed `df -B1 -P /root/share/container-workspaces/hrl-174-new`; exit=0; timed_out=False.
8. Executed `findmnt -T /root/share/container-workspaces/hrl-174-new -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
9. Executed `df -B1 -P /root/share/container-workspaces/hrl-174-new/workspace`; exit=0; timed_out=False.
10. Executed `findmnt -T /root/share/container-workspaces/hrl-174-new/workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
11. Executed `df -B1 -P /root/share/mnt164`; exit=0; timed_out=False.
12. Executed `findmnt -T /root/share/mnt164 -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
13. Executed `id`; exit=0; timed_out=False.
14. Executed `hostname`; exit=0; timed_out=False.
15. Executed `which ssh`; exit=0; timed_out=False.
16. Executed `which rsync`; exit=0; timed_out=False.
17. Executed `which lsof`; exit=0; timed_out=False.
18. Executed `which fuser`; exit=1; timed_out=False.
19. Executed `which ionice`; exit=0; timed_out=False.
20. Executed `which docker`; exit=1; timed_out=False.
21. Executed `which nsenter`; exit=0; timed_out=False.
22. Executed `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 admin-wcx@10.208.130.164 'hostname; id; df -B1 -P /home/shared; findmnt -T /home/shared; stat /home/shared/huangrulin'`; exit=255; timed_out=False.
23. Executed `timeout 45 nice -n 19 ionice -c 3 du -x -B1 --max-depth=1 /tmp`; exit=0; timed_out=False.
24. Executed `find /root/workspace/accel-sim-framework/.git/objects/pack -maxdepth 1 -type f -printf '%f	%s	%T@
'`; exit=0; timed_out=False.
25. Executed `find /root/workspace/accel-sim-framework/.git -maxdepth 1 -name '*.lock' -printf '%f	%s	%T@
'`; exit=0; timed_out=False.
26. Executed `df -B1 -P /tmp`; exit=0; timed_out=False.
27. Executed `findmnt -T /tmp -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
28. Executed `df -B1 -P /root/workspace`; exit=0; timed_out=False.
29. Executed `findmnt -T /root/workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.
30. Executed `df -B1 -P /root/share/container-workspaces/hrl-174-new/workspace`; exit=0; timed_out=False.
31. Executed `findmnt -T /root/share/container-workspaces/hrl-174-new/workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT`; exit=0; timed_out=False.

## Deferred actions

- rsync dry-run, copy, source/remote SHA256, remote receipt, exact-source stability check: NOT_RUN (both precheck gates blocked).
- tmp_pack fsck/unique-object inspection: NOT_RUN (actual source Git directory inaccessible).
- Any source cleanup, permission change, process stop, lane result/registry/worktree write: NOT_RUN.
- Local build_receipt.py generated the derived JSON/CSV/Markdown files; its receipt SHA256 values are not data archive verification.
- git diff --check, explicit receipt-path staging, commit, push, fetch and remote readback are recorded after execution in PUBLICATION.json.
