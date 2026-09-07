# Source and artifact anchors

Snapshot time: `2026-09-07T10:40:57+08:00`.

| Artifact | Immutable anchor |
| --- | --- |
| Framework integration source | `a7c0759be7f293ed0d5e2179c62094b6de49c1e8` |
| Core integration source | `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` |
| Simulator binary SHA-256 | `100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda` |
| Runtime `libcudart.so` SHA-256 | `d0da41ae1323cf4eeb610123d69d7714124cfe5ebfcc4e45f02b910e51c57ee6` |
| Active ROI/profile | `prefill` / `generic` |
| Generic VM source config SHA-256 | `13e3952bda1b9390419388ce81b296785bc0b1200e3755922eb6ff0b2ac52caa` |
| Materialized generic formal config SHA-256 | `8a9a92a8743ee1c4797faabe588ef13dff039dc84b678a07849f4bfb8ebe4579` |
| Prefill object map SHA-256 | `7ec6e868f8190ba6493124cb518753ccc7d14cbbd2ad169777cac9fbd6742a85` |
| Immutable prefill kernel-list SHA-256 | `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` |

At snapshot both C3 source worktrees were clean.  The running simulator was
therefore bound to the source heads and binary above.  This review branch is
separate from the frozen C3 worktree; its docs-only commit must not be
misattributed to any completed or running C3 arm.
