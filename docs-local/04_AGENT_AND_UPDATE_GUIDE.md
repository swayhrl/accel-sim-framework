# Agent and update guide

Mandatory preflight:
```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git remote -v
```
Chat titles are not authority; physical worktree, branch and HEAD are. Framework and nested GPGPU-Sim are separate Git repositories. Keep simulator behavior changes separate from packaging. Recover/update history from `cache/git/framework-offline-sim-v1.0.bundle` and `cache/git/gpgpu-sim-project-offline-sim.bundle`, verify SHA, then fetch/cherry-pick selectively after review; do not merge research branches automatically.
