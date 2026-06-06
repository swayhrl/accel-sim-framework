# Clean Baseline Pipeline

Clean baseline validation must start from a committed tree.

Required sequence:

```bash
git status --short
bash scripts/accelsim/a7a_clean_baseline_hardened.sh
```

`git status --short` must print nothing before the rebuild starts. If tracked files change after that, commit the changes and rerun the baseline from the beginning.

Status meanings:

- `PASS_CLEAN_DIFF_ZERO`: build strings contain `_modified_0`, `_modified_0.0`, or equivalent zero diff count, and git status was clean.
- `PASS_NO_DIRTY_MARKER`: no dirty or modified marker was found.
- `FAILED_DIRTY_TREE`: the tree was dirty before build.
- `FAILED_DIRTY_BUILD_STRING`: a dirty token or nonzero modified count was found.
- `NEEDS_REVIEW_VERSION_STRING`: a suspicious build string could not be parsed.

Reports and stats live under `.local_reports/`; logs live under `.local_logs/`. Review packs are generated under `review_packs/`.
