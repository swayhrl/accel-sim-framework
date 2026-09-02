# Open issues

## BLOCKED_REMOTE: no verified writable Core remote

The Core repository config contains only:

```text
origin https://github.com/accel-sim/gpgpu-sim_distribution.git
```

This is the official project repository and was not pushed to. The candidate
`git@github.com:swayhrl/gpgpu-sim_distribution.git` returned “Repository not
found” / unreadable under the authenticated account. No other Core fork remote
was configured locally. A Core branch/worktree exists locally, but it cannot yet
be pushed to a traceable writable remote.

Action required: provide or create a sanctioned writable Core fork/remote, then
verify it with a non-mutating dry-run before any source implementation begins.

## Scope gate

S1-R1 semantic specification and all TLB/PTW/page-table implementation remain
out of scope. Do not advance while the remote issue is unresolved.
