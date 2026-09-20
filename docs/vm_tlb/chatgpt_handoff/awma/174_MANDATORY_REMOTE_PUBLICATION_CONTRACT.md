# AWMA 174 Mandatory Remote Publication Contract

Date: 2026-09-20
Status: MANDATORY

All future AWMA Goals on 174/174-new must complete remote publication before STOP.

Required closeout:

```text
science/engineering closure
-> node164 durable closure
-> report + review pack
-> SHA256SUMS
-> commit
-> push
-> git fetch origin
-> remote HEAD == local HEAD
-> remote tree contains all promised files
-> worktree clean
-> STOP
```

A local-only commit, worktree-only artifact, or node164-only artifact is not a complete stage.

Every final 174 report must state:

- execution branch;
- local HEAD;
- remote HEAD;
- remote/local equality;
- report path;
- review-pack path;
- remote-tree verification status;
- worktree clean status.

If a ref is lost, republish the exact accepted commit object under a recovery ref.

Publication failure is an engineering/provenance issue and never authorizes simulation rerun.

Long 174 campaigns must reserve sufficient final time for hashing, commit, push, remote verification, and tree inspection.
