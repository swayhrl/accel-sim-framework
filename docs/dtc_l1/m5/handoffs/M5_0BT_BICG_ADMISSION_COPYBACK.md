# M5.0BT — BICG storage admission and copyback receipt

Status: `PASS` for the BICG-bound admission and BICG immutable-store copyback.
This does not make T2 replay-qualified and does not admit a formal result.

| item | evidence |
| --- | --- |
| source bundle | `ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33` |
| source archive | `bicg.tar.zst`; 43,146,784 bytes; SHA-256 `cdc0a9f540c85a2d43dab5ac77ccda924ddecb16c3e5ddd4f1b5c8652422f31e` |
| BICG byte measurements | raw 416,485,958; grouped 305,558,210; working headroom 722,045,659 bytes |
| capture-volume free space | 104,537,268,224 bytes on the designated data volume at measurement |
| initial admission | `STORAGE_ADMISSION.json`: `PASS`; BICG bundle/archive-bound; safety factor 32; projected 47,591,571,552 bytes, below measured free space |
| transfer | archive destination SHA-256 equals source archive SHA-256 |
| immutable store | `/workspace/m5-trace-immutable/archives/bicg.tar.zst`; unpacked once to `/workspace/m5-trace-immutable/bicg` |
| destination validation | internal bundle `SHA256SUMS` revalidation `PASS`; local transfer receipt records `TRANSFER_PASS` with the exact bundle and archive identities |

The BICG measurement is not a credible upper bound for the Paper-10 trace
set: its two `(16,1,1) x (256,1,1)` invocations do not bound 2DConv's
`(128,512,1) x (32,8,1)` geometry. Per the runbook, an exact 2DConv
representative/heavy capture will update this provisional admission before the
remaining queue is admitted. This is a storage-fidelity diagnostic only; it
does not alter BICG's accepted immutable payload or permit reuse of older
execution-driven measurements as trace-replay results.

T2 may use the BICG bundle now, under its independent same-bundle Base/IO/OO
HARD gates. The heavy capture runs independently on the V100 capture host;
neither task modifies the BICG archive or its immutable-store copy.
