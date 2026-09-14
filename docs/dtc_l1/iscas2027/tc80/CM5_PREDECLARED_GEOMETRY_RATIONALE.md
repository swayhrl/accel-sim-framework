# CM5 predeclared exact-80-KiB diagnostic geometry

This is a pre-result geometry decision, not a performance-selected baseline.
CM5 is mandatory irrespective of CM3 performance because the canonical
primary TC80 geometry is 32 sets × 20 ways: its associativity exceeds eight,
and CM0 proves multiple exact-80-KiB source-legal factor pairs.

The single bounded diagnostic uses `128 sets × 5 ways × 128 B = 640 lines =
81,920 B`. It is selected from CM0's legal power-of-two set-count candidates
before any TC80 primary result exists. Relative to the primary 32×20 it
changes the set mapping and lowers associativity while preserving exact data
capacity, line size, conventional tag/data semantics, queues, policies,
banks, L1 latency, Paper-Base PIB=8, and effective MSHR=32.

The planned workload set is exactly the contract's representative `BICG`,
`Btree`, and `2DConvolution`. These CM5 rows will be labeled robustness
diagnostics and excluded from the CM3 FAST12 summary and every primary GM.
