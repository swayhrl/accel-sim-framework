# C16 A fixed-release manifest validation

The previous `G@b5039e…` / `C@fed28d…` rows are historical local-prep
evidence only. They are not substituted for the re-consumption required before
C16-0.9. The current fixed candidates were independently read from Git objects
and re-hashed as follows.

| Producer | Candidate commit | Manifest SHA-256 | Payload validation | Consumption result |
| --- | --- | --- | --- | --- |
| G | `45e293b84940ef59b7b134bcda48aca7d0b99b2f` | `7c18c2a806ac37b974702050567430f83f10bbdacc78c5af2fe09ea871896087` | 17/17 release payload byte counts and SHA-256 values match; all 66 local wheel paths, byte counts, and SHA-256 values named by the fixed wheelhouse manifest also match. | Final-consumed as offline environment/wheel/runner infrastructure only; no GPU runtime result. |
| C | `29e669eca19ac3b2a1350bf2d097569a41f123e1` | `14a7c02985d13203bf90d251751ae6ab50c3159ce28e439b51917e05204f9f04` | 24/24 manifest payload byte counts and SHA-256 values match. | Final-consumed offline selector protocol only, not a native fact table. |
| H | `932c6fa44a4896265214fc2136e34698402a5c7f` | `b78212310628b479e78636c3d7b42ea4a4d5d9d635115e8b7af79e05b4a88d9c` | Four `code_sha256` payloads plus root-relative `TEST_RECEIPT.json` match. | Final-consumed offline admission protocol only. Manifest has no dynamic scientific rows. |

Therefore the fixed G wheel/environment/runner package and C/H offline
protocols may be named in A's future package, but no new G/C/H scientific
data or transfer/rental authorization has been inferred from a live worktree
or partial release.
