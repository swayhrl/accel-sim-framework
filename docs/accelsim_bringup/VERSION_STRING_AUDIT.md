# Version String Audit

Accel-Sim and the embedded GPGPU-Sim build strings in this repository include a `_modified_` token generated from git diff counters in `version_detection.mk`.

Observed clean-tree examples:

```text
accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49
gpgpu-sim_git-commit-6c3cf4ff_modified_0.0
```

The token name is misleading: `_modified_0.0` means the makefile's diff-count field is zero. It should be treated as clean only when `git status --short` is empty at build start and build end.

Accepted clean forms:

- `_modified_0`
- `_modified_0.0`
- `_modified_0.00`
- no `modified` or `dirty` token

Rejected dirty forms:

- `dirty`
- `_modified_1`
- `_modified_1.0`
- `_modified_2`
- `_modified_<nonzero>`

Suspicious forms that cannot be parsed numerically should be marked `NEEDS_REVIEW_VERSION_STRING`.

A6B updates `scripts/accelsim/a6_clean_baseline_rerun.sh` to parse build strings rather than grepping for `modified`. The clean-tree requirement is still mandatory.
