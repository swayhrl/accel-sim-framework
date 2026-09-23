# SG5 execution review status (V4)

Snapshot time: `2026-09-23T00:24:32Z`.

`SG5_EXECUTION_DATA_SNAPSHOT_V4.tsv` contains the 17 paper-critical
observer-ON strict-PASS rows presently available: complete BICG and Btree
normal/IO/OO coverage, complete 2DConvolution normal/IO/OO coverage, and the
available GESUMMV normal plus TC80-S sector anchor rows.

The GESUMMV IO and OO observer-ON attempts exited `-9` and their strict
receipts are preserved as FAIL. They have no accepted cycle, instruction, or
traffic result and are deliberately absent from the snapshot. The predeclared
paper-critical matrix remains unchanged; this is a review snapshot, not a
result-driven reduction.
