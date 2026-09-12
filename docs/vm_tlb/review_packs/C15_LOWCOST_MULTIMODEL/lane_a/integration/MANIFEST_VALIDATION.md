# Hash-bound cross-lane input validation

Consumer: lane A at the fixed planning SHA
`9a755b14b01c5a77a6fc98c2547616e1c490e806`.

| Producer | Fixed remote commit | Manifest SHA-256 | Result |
| --- | --- | --- | --- |
| B | `721e30f377dab36d826dc7ea9d47e11c5d85aa5c` | `38dcc5c615d531b6c812facffa5b0634b1bafff89b87a57e190a2fca8cdc7aad` | PASS |
| C | `a51d6c91b1e7d7df27a4af80823a29ff30bb9806` | `17d7888650c2c51f1dd0d4a418eb45948212a259dd01661d1adca33832e5dec0` | PASS |

For each producer, lane A read the manifest from the named immutable commit,
checked that the manifest planning SHA is the common handoff SHA, then recomputed
SHA-256 for every payload selected in `CONSUMED_INPUTS.tsv`. Each selected digest
matches the digest declared by that producer's manifest. No producer working tree,
uncommitted file, live partial result, or branch ref was used as evidence.

The consumed files remain in their producer commits; this lane publishes only the
identities, manifest hashes, validation result, and bounded synthesis. This is a
read-only cross-lane consumption record, not a merge and not a claim that A ran
native capture, a GPU workload, a simulator, or a dynamic measurement.
