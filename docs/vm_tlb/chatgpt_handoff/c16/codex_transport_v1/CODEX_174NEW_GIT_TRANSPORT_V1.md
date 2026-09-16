# C16 Codex Git transport closure V1

IMPORTANT: Execute this task in GOAL MODE.

## Objective
Close the already-produced V19R1 worktree/results all the way to the canonical GitHub repository, prove the canonical remote branch exists, and establish the transport protocol that must be used by future Codex Goals.

Do not rerun the V19R1 scientific audit unless its artifacts are genuinely missing. Do not ask the user for manual Git intervention.

## Canonical repository
The authoritative repository is exactly:

`swayhrl/accel-sim-framework`

Acceptable canonical Git URLs are:

- `git@github.com:swayhrl/accel-sim-framework.git`
- `https://github.com/swayhrl/accel-sim-framework.git`

Do not treat `LOCAL == origin` as sufficient until the resolved `origin` URL is proven to be this canonical repository.

## Known 174-new Codex tool issue
The command runner has previously returned exit code 0 with empty captured stdout/stderr. Therefore:

- empty captured stdout alone is not evidence that a command did not execute;
- use explicit absolute worktree paths;
- redirect diagnostic command output to `/tmp/...` and read the files when necessary;
- do not use SSH to node164 for data access; use `/root/share/mnt164` directly;
- Git transport to GitHub may use the canonical SSH URL above.

## Required V19R1 branch and artifacts
Implementation branch:

`hrl/c16-qwen3-kv-scope-audit-174new-v19r1`

Expected review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_KV_SCOPE_AUDIT_174NEW_V19R1/`

Expected analysis script:

`util/vm_tlb/c16/analysis/v19r1.py`

Required scientific outputs include:

- `KV_SCOPE_AUDIT.json`
- `NONZERO_SHARD_KV_SCOPE.tsv`
- `SHA256SUMS`

## Stage A — locate the actual V19R1 worktree
Use the repository's worktree registry. Do not assume the main worktree contains V19R1.

Record for each candidate:

- worktree absolute path
- branch
- HEAD
- `git status --short`

Select only the worktree containing the V19R1 review pack above.

## Stage B — verify scientific closure before transport
From the actual V19R1 worktree:

1. Run `python3 -m py_compile util/vm_tlb/c16/analysis/v19r1.py`.
2. Verify `SHA256SUMS` from the review pack directory.
3. Read and preserve the literal `scope_classification` from `KV_SCOPE_AUDIT.json`.
4. Confirm all 8 nonzero shards are present in `NONZERO_SHARD_KV_SCOPE.tsv`.
5. Do not alter the scientific result merely to satisfy transport closure.

If correct V19R1 files are uncommitted, commit only those files. If they are already committed, do not create a duplicate commit.

## Stage C — diagnose the current remote before any push
Record all of the following to `/tmp/c16_v19r1_transport_diag.txt`:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git remote -v
git remote get-url origin || true
git config --get remote.origin.url || true
```

Read the file back and determine whether `origin` resolves to the canonical repository.

If `origin` is not canonical, do not overwrite it blindly because other worktrees/tasks may rely on repository configuration. Instead push using an explicit canonical URL.

## Stage D — push exact HEAD to the canonical GitHub repository
Preferred transport is the canonical SSH URL if current credentials support it:

```bash
CANONICAL='git@github.com:swayhrl/accel-sim-framework.git'
BRANCH='hrl/c16-qwen3-kv-scope-audit-174new-v19r1'
LOCAL=$(git rev-parse HEAD)

git push "$CANONICAL" "HEAD:refs/heads/$BRANCH"
```

If canonical SSH transport itself fails for an authentication/network reason, use the canonical HTTPS URL only if the existing credential setup permits it. Do not substitute a fork, local bare repository, mirror, or different owner/repository.

## Stage E — canonical remote verification
Verification must use the canonical repository URL, not merely the alias `origin`:

```bash
REMOTE=$(git ls-remote "$CANONICAL" "refs/heads/$BRANCH" | awk '{print $1}')
printf 'LOCAL=%s\nREMOTE=%s\n' "$LOCAL" "$REMOTE" > /tmp/c16_v19r1_canonical_remote.txt
cat /tmp/c16_v19r1_canonical_remote.txt
test -n "$REMOTE"
test "$LOCAL" = "$REMOTE"
```

Completion requires all three:

1. canonical repository identity proven;
2. canonical branch ref exists;
3. canonical remote HEAD exactly equals the actual V19R1 worktree HEAD.

`LOCAL == origin` without canonical repository identity is not a valid completion condition.

## Permanent transport rule for future Codex Goals
Future C16 handoffs must end with this transport closure contract:

1. operate from the actual Goal worktree;
2. commit only Goal-owned changes;
3. identify the canonical repository before push;
4. push `HEAD:refs/heads/<implementation-branch>` to canonical GitHub;
5. verify with `git ls-remote <canonical-url> refs/heads/<implementation-branch>`;
6. require nonempty remote ref and exact local/remote SHA equality;
7. report literal local HEAD, canonical remote HEAD, canonical remote URL, branch and worktree path;
8. never ask the user to perform normal commit/push/verification steps that Codex can execute itself.

## Final report
Report only after the entire Goal is closed:

```text
worktree:
implementation branch:
local HEAD:
canonical remote URL:
canonical remote HEAD:
canonical remote match: PASS/FAIL
origin URL:
origin canonical: YES/NO
review pack:
scope classification:
nonzero shard count:
CTA coverage summary:
KV_POST_UPDATE_K membership summary:
final decision:
```

If canonical transport is genuinely blocked after bounded SSH/HTTPS checks, preserve all scientific evidence and report the exact transport failure. Do not claim success based only on a noncanonical `origin`.

STOP only after canonical GitHub closure or a genuine canonical transport blocker.
