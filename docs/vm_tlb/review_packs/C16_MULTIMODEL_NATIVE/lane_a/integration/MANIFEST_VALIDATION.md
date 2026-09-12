# C16 A fixed-release manifest validation

| Producer | Artifact commit | Manifest SHA-256 | Payload validation | Result |
| --- | --- | --- | --- | --- |
| G | `b5039e160331db993e226bc02fcdfa811db29911` | `97b54c7cc7462822fa65caa59ffc3c9de467d0bfefcf79e688b8814895f7d497` | 11/11 manifest payload SHA-256 and byte counts match; 19 `util/` package SHA rows in its package manifest also match the producer commit. | PASS |
| C | `fed28d8113c0d92cf3a576645f5d736769aefb12` | `20b94eef486b04832994e0def4a5d480becaf606dfd065a8fba969ecc877f138` | 22/22 manifest payload SHA-256 and byte counts match. | PASS |
| H | `65b5357400db3b4c77f8a60e575091e22fb081ee` | `NA` | No H `PUBLISH_MANIFEST.json` or equivalent hash-bound release exists at this commit. | REJECTED — NOT CONSUMED |

Only the two PASS rows are C16 A inputs.  G's release is offline infrastructure,
not native evidence; C's release includes offline fixture and historical-oracle
boundaries, not a native fact table.  H's visible commit was not used to infer a
metric, readiness result, or package component because the required manifest
closure is absent.
