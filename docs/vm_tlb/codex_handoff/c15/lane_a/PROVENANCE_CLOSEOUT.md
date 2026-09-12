# C15 lane A provenance-only handoff closeout

Status: `C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_FINAL_REVIEW`.

This closeout records provenance roles for the semantic repair without changing
any Weight/KV numeric fact, starting a GPU, simulator, SASS, or full-ROI task, or
adding a dynamic conclusion.

| Role | Immutable identity | Meaning |
| --- | --- | --- |
| Planning authority | `9a755b14b01c5a77a6fc98c2547616e1c490e806` | C15 authorization and common contract; retained as `planning_sha`. |
| Static producer checkpoint | `9bdb692dfda2a9b42578133b97a84283fed9d34a` | Original bounded multi-model static fingerprint publication. |
| Integration producer checkpoint | `a69ee630a8e3bc509029edc5d27c2daf7d2089f4` | Original A-owned hash-bound B/C integration publication. |
| Semantic-repair producer implementation | `e5b25da3a7eb7ccb09ee9a1f3fd1c6b66b0313e6` | Code/test checkpoint that produced the corrected provenance and semantic artifact. |
| Artifact checkpoint | `4b6acb461940f504a13ad03c321a6a1a808f15fd` | Exact A artifact checkpoint: corrected registry fields, alias audit, terminology, B role mapping, limits, receipt, and manifest. |
| Final handoff HEAD | `refs/heads/hrl/vm-c15-static-v0` | Resolve this branch after fetching; it carries this closeout and remains distinct from the artifact checkpoint. |

B consumption is also role-separated: A validates the B manifest and four
selected payload hashes at artifact checkpoint
`57e2ef203befc96cfcefe00de2aaf8b0baab5d8b`; B final handoff HEAD
`721e30f377dab36d826dc7ea9d47e11c5d85aa5c` is recorded only as the final
provenance closeout carrier.

The corrected artifact passed 13 unit tests, static fixture tests, schema and
manifest validation (T01/T03–T06/T14/T18/T20/T22). A rejected 29-field registry
row was corrected before acceptance and remains recorded as a corrected cost
attempt. No full weight was downloaded.
