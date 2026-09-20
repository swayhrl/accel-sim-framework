# AWMA 174 Mandatory Remote Publication Contract

Date: 2026-09-20

Scope:

All future Codex Goals executed on node 174 / 174-new for the AWMA mainline.

Status:

`MANDATORY_CLOSEOUT_CONTRACT`

## 1. Core rule

A 174 Goal is NOT complete when local files, node164 artifacts, or a local Git commit exist.

A Goal may emit its final COMPLETE marker only after the accepted scientific/provenance closure is remotely published and independently verifiable through the GitHub remote.

Required sequence:

```text
science/engineering closure
-> node164 durable closure / ACK
-> report + review pack
-> SHA256SUMS
-> git status audit
-> commit
-> push
-> git fetch origin
-> remote HEAD == local HEAD
-> remote tree contains required report/review-pack files
-> worktree clean
-> STOP
```

## 2. Remote branch publication

Every execution Goal must define an execution branch name before work starts.

At closeout:

- push the exact final execution HEAD to that branch;
- do not leave the accepted result only as a local commit;
- do not rely on the existence of another child commit to make the result indirectly reachable;
- do not delete the execution ref during the same stage.

If the originally intended branch ref cannot be created or was deleted:

- immediately publish the exact same accepted commit object under a recovery ref;
- record the recovery ref and commit SHA;
- continue closeout without rerunning science.

## 3. Required remote verification

After push, Codex must independently verify:

- `git rev-parse HEAD`
- `git rev-parse origin/<execution-branch>`
- exact SHA equality;
- expected parent/ancestry where relevant;
- remote tree contains the final report;
- remote tree contains the complete review pack;
- remote tree contains matrix/metrics/receipts/SHA files promised by the report.

A local path printed in the final message is not sufficient evidence.

## 4. Report/pack consistency

The final user-facing report must not claim that an artifact is "written into the pack" unless the remote tree actually contains it.

Before final response, compare the claimed deliverables against the remote tree.

If an artifact exists only on node164 or only in the worktree:

- classify the stage as `PROVENANCE_CLOSEOUT_REQUIRED`;
- publish it before emitting final COMPLETE whenever time permits.

## 5. No science rerun for publication failure

Missing remote publication is an engineering/provenance issue.

Do NOT rerun accepted simulations merely because:

- branch push was missed;
- ref was deleted;
- report/pack was not committed;
- SHA index needs regeneration from immutable raw evidence.

Recover/publish existing evidence instead.

## 6. Deadline behavior

The final closeout reserve must include sufficient time for:

- hashing;
- Git commit;
- push;
- remote fetch/verify;
- remote-tree inspection.

Do not consume the entire deadline with simulation and leave publication outside the campaign window.

For long unattended 174 campaigns, reserve at least the final hour for closure unless a stricter stage contract requires more.

## 7. Final response requirement

Every final 174 Codex report to the user must include:

- execution branch;
- final local HEAD;
- final remote HEAD;
- explicit statement `remote HEAD == local HEAD`;
- report path;
- review-pack path;
- remote-tree verification status;
- worktree clean status.

If any of these is missing, the stage is not considered fully closed.

## 8. Future handoff requirement

Every future ChatGPT-authored 174 Goal must either:

- reference this contract explicitly; or
- embed equivalent publication requirements directly.

This rule applies independently of the scientific task.
