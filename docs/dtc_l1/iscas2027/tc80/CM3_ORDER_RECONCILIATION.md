# CM3 FAST12 order reconciliation

This record resolves a textual ordering discrepancy before the CM3 primary
campaign starts. It neither launches a simulator nor changes a frozen input.

## Hash-bound evidence

| source | SHA-256 | terminal two primary rows |
| --- | --- | --- |
| frozen Lane-A accepted performance input, `paper_primary_performance.tsv` | `a4f3b08b01dff497af0c22e2212b893f59e3a3210357cf0831c951677f719c66` | `NN`, then `MRI-Q` |
| TC80 frozen workload authority | `662d8973a5ff34e6039a7823b4417ba8be38bd5b13348aa779defa1356837a62` | ordinal 11 `NN`, ordinal 12 `MRI-Q` |
| scientific handoff | `ad523fd66fcd4e59f695dcd1da4597284d24af2de8cc279094e15d6190b6b25e` | requires the exact same FAST12 order as frozen FAST64 |
| execution contract | `293fcafa71ded61aae008bbb489ca72b9ab8dd98e225f213b10a1e572b21da6c` | says its list is from the frozen FAST12 authority |

The execution contract's rendered list at §7.1 instead places `MRI-Q` at 11
and `NN` at 12. That ordering is inconsistent with the frozen authority it
names and with the scientific handoff. It is a transcription inconsistency,
not an unapproved scientific design choice.

## Source-correct resolution

CM3 will use the unique order carried by the hash-bound authority, not a
hard-coded reordering:

`ATAX, BICG, GESUMMV, GEMM, 2DConvolution, Btree, DWT2D, Gaussian, Hotspot1, LUD, NN, MRI-Q`.

The evidence materializer rejects an authority unless it has exactly the 12
accepted members and contiguous ordinals 1 through 12. CM3's run manifest,
summary, input/output binding table, and final independent validator will all
use that recorded order. No workload is added, removed, or reordered relative
to frozen FAST64 evidence.
