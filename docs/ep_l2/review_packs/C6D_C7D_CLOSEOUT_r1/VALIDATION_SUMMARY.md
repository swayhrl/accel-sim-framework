# Validation summary

This is a review-only inventory. It separates evidence reproduced by the
packaging audit from historical/diagnostic evidence; it does not promote an
old run to the final C7d source pair.

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| C6d bank directed regressions | PASS (historical C6d closeout) | C6d smoke outcomes are listed in `C6D_SMOKE_COMPARISON.csv`; corrected counters have no structural retry in zero-contention cases. |
| C7d schema/parser regression | PASS (source-level C7d evidence) | `tests/ep_l2/test_epl2_schema.cc`; Framework parser test updated in the final commit range. Compact command output was not retained. |
| C7d analyzer regression | PASS (source-level C7d evidence) | Analyzer preserves `NOT_EMITTED_BY_EPL2B0V1` rather than mapping coarse fields. Compact command output was not retained. |
| Kernel bank interval deltas | PASS (producer/source review; diagnostic natural sample) | Kernel records carry launch-to-completion bank deltas; sample has per-kernel values. Final-pair execution evidence is missing. |
| 5K window parser path | PASS (source/parser review) | `scope=window` is emitted/parses to `target_window.csv`; diagnostic sample is a short workload with no completed 5K window, hence file contains only header. |
| Terminal invariants | PASS for all four C6d smoke pairs | Each summary reports payload consistency and terminal-clean = 1; see C6D CSV. |
| Full Release build on final source pair | NOT RETAINED | No compact final-SHA build transcript was found in the C7d worktree. |
| C3-C7 + C6d final combined regression transcript | NOT RETAINED | Existing historical C5-C7 closeout is not a final-C7d validation artifact. |
| Instrumentation OFF vs ON timing neutrality, final source pair | NOT RETAINED | Required exact cycle/instruction/transaction comparison is absent. |
| Host-overhead measurement | NOT RETAINED | Required short/medium comparison is absent. |
| `git diff --check` over C7d ranges | PASS | Packaging audit completed with no output for Core `0cde3333..88e243e8` and Framework source range. |
| Source worktree cleanliness | CONDITIONAL | Core clean. Framework has untracked validation output directories; no source changes are staged and generated outputs are excluded from Git. |

The missing retained evidence is a reproducibility/readiness issue, not a
claim of a simulator correctness bug. It blocks the final 26-run launch until
review resolves it or the exact final-source validation is rerun and captured.
