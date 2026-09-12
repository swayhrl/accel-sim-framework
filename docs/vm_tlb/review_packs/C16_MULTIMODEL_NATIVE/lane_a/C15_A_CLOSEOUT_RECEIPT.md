# C15-A provenance and metadata closeout receipt

Status: `PASS — C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_FINAL_REVIEW`.

This C16 receipt consumes C15 as immutable, read-only evidence.  It does not
rewrite C12–C15 scientific content, alter any Weight/KV value, download a full
weight, or start a GPU, profiler, NVBit, simulator, SASS, or full-ROI task.

| Role | Immutable identity | C16 A verification |
| --- | --- | --- |
| C15 planning authority | `9a755b14b01c5a77a6fc98c2547616e1c490e806` | Recorded separately from C16 planning and producer checkpoints. |
| A static producer checkpoint | `9bdb692dfda2a9b42578133b97a84283fed9d34a` | Preserved from the C15 A closeout. |
| A integration producer checkpoint | `a69ee630a8e3bc509029edc5d27c2daf7d2089f4` | Preserved from the C15 A closeout. |
| A semantic-repair implementation | `e5b25da3a7eb7ccb09ee9a1f3fd1c6b66b0313e6` | Preserved as implementation provenance only. |
| A artifact checkpoint | `4b6acb461940f504a13ad03c321a6a1a808f15fd` | Its 34 manifest payloads were rehashed; all match. |
| A final handoff HEAD | `252f5fedbd4fe816167b9f476bba713563d54a3e` | Read only as final handoff/closeout carrier; not substituted for the artifact. |
| B artifact checkpoint | `57e2ef203befc96cfcefe00de2aaf8b0baab5d8b` | Its 21 manifest payloads were rehashed; all match. |
| B final handoff HEAD | `721e30f377dab36d826dc7ea9d47e11c5d85aa5c` | Recorded only as B's final provenance carrier. |
| C artifact and final handoff | `a51d6c91b1e7d7df27a4af80823a29ff30bb9806` | Its 35 manifest payloads were rehashed; all match. |

Manifest SHA-256 values rechecked directly from their artifact commits:

- A: `8276847397acbe2d45e03b0b9eb81bbde6a82870dfb86666532f54d5c8dca351`
- B: `38dcc5c615d531b6c812facffa5b0634b1bafff89b87a57e190a2fca8cdc7aad`
- C: `17d7888650c2c51f1dd0d4a418eb45948212a259dd01661d1adca33832e5dec0`

The CPU-only C15 verifier was rerun after immutable-payload verification:
`--selftest` reported T03/T04/T05/T06 PASS; `--validate` reported
T01/T14/T20/T18/T22 PASS; and 11 C15 A unit tests passed.  This is a schema and
provenance revalidation in the C16 planning tree, not a new C15 result.

The inherited repair semantics remain binding: a missing header cannot be
labelled `CONFIG_AND_HEADER_CONSISTENT`; config tying and exact file-range alias
evidence are separate; a tied config with one stored embedding is not itself a
divergence; `physical_bytes` means legacy *checkpoint-file storage* column name,
never GPU physical address/storage; and MoE `intermediate_sizes` is not a full
routed/shared-expert width description and must not drive MoE clustering.
