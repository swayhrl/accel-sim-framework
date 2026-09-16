# C16 174-new Codex canonical Git transport visibility proof

## Goal
Close the transport gap once and for all, without rerunning scientific analysis.

The V19R1 scientific work already exists locally. This task must make its implementation branch verifiably visible in the canonical GitHub repository and persist a durable transport receipt on a branch already known to be visible.

Canonical repository URL:

`https://github.com/swayhrl/accel-sim-framework.git`

V19R1 implementation branch:

`hrl/c16-qwen3-kv-scope-audit-174new-v19r1`

Expected V19R1 review pack:

`docs/vm_tlb/review_packs/C16_QWEN3_KV_SCOPE_AUDIT_174NEW_V19R1/`

Visible transport coordination branch:

`hrl/c16-codex-transport-174new-v1-coordination`

## Known tool issue
174-new Codex may occasionally lose captured stdout/stderr. Therefore all decisive outputs must also be written to files under `/tmp`, then copied into a durable JSON receipt committed to Git.

Do not use SSH as a fallback. Use local Git plus the canonical HTTPS repository URL explicitly.

## Required procedure

1. Locate the actual V19R1 worktree by searching `git worktree list --porcelain` for a worktree containing the V19R1 review pack. Do not assume the main worktree.

2. In that worktree record:
   - current branch
   - local HEAD
   - `git status --short`
   - literal `scope_classification` from `KV_SCOPE_AUDIT.json`
   - SHA256 verification status
   - `python3 -m py_compile util/vm_tlb/c16/analysis/v19r1.py`

3. Inspect and record remote configuration:

```bash
git remote -v > /tmp/v19r1_remote_v.txt 2>&1
git remote get-url origin > /tmp/v19r1_origin_url.txt 2>&1
```

4. Push the actual V19R1 worktree HEAD using the literal canonical URL, not an alias:

```bash
git push https://github.com/swayhrl/accel-sim-framework.git \
  HEAD:refs/heads/hrl/c16-qwen3-kv-scope-audit-174new-v19r1 \
  > /tmp/v19r1_push_stdout.txt 2> /tmp/v19r1_push_stderr.txt
PUSH_RC=$?
```

5. Verify with the literal canonical URL, independent of `origin`:

```bash
git ls-remote https://github.com/swayhrl/accel-sim-framework.git \
  refs/heads/hrl/c16-qwen3-kv-scope-audit-174new-v19r1 \
  > /tmp/v19r1_lsremote.txt 2> /tmp/v19r1_lsremote.err
LSREMOTE_RC=$?
```

Require exactly one non-empty ref line and require its SHA to equal local HEAD.

6. Independently verify public GitHub REST visibility. URL-encode the branch name using Python and query the canonical GitHub API. Save HTTP status and response body to files. If the repository/API requires authentication and unauthenticated REST cannot see it, record that typed condition; do not treat it as branch absence if canonical `git ls-remote` is positive.

7. Create a durable JSON receipt containing at least:
   - canonical_repository_url
   - implementation_branch
   - local_head
   - origin_url
   - canonical_lsremote_head
   - push_rc
   - lsremote_rc
   - github_rest_http_status
   - scope_classification
   - review_pack_path
   - sha256sums_pass
   - py_compile_pass
   - timestamp_utc

8. Commit that receipt to the already-visible transport coordination branch under:

`docs/vm_tlb/transport_receipts/C16_174NEW_V19R1_CANONICAL_TRANSPORT.json`

Use a separate clean worktree for the transport coordination branch if necessary. Push that receipt commit using the same literal canonical HTTPS URL.

9. Verify the transport coordination branch itself with canonical `git ls-remote` and require local receipt commit HEAD == canonical remote HEAD.

10. Only after both checks pass, report:
   - V19R1 local HEAD
   - canonical V19R1 remote HEAD
   - transport receipt commit HEAD
   - literal scope classification

Do not rerun V19R1 scientific analysis. Do not run GPU. Do not modify accepted raw/catalog.

This task is complete only when the V19R1 implementation ref and the durable transport receipt are both canonically visible, or when a specific reproducible transport blocker is proven with preserved stdout/stderr and HTTP evidence.