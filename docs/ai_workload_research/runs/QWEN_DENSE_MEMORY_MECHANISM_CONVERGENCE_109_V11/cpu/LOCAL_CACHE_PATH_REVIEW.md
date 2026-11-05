# Local cache path: offline SASS review

Both completed LOCAL reports expose SASS through NCU2025.1.1 offline import. Each selected-result export completed within 30 seconds and 2 MiB; no target process, CUDA query, running Lt report or GPU experiment was used.

B1 visibly contains `LDG.E.EF.U16` and `LDG.E.U16.STRONG.SM`. B2 visibly contains `LDG.E.LTC128B.128`. These are observed modifier strings only. This review does not assign cache/eviction semantics to them or establish which loads access the weight.

First REUSE and EVICT normalized instruction sequences match within each report. Static opcode counts are instruction positions, not executed counts. The two batch modes use different implementation paths; those differences are a useful mechanism clue alongside the recorded DRAM contrast, but do not prove the causal cache policy.

Operand-to-weight attribution and architecture-validated EF/STRONG.SM/LTC128B semantics remain UNKNOWN. No L1 bypass, L2 persistence, hit rate, eviction-first behavior or model-wide bottleneck is inferred from opcode spelling.

JSON records exact commands, bounded-output receipts and hashes, report/source SHA256, representative instruction lines, complete lexical opcode histograms, first-pair comparison, recorded 5-pair DRAM ranges and CPU RSS. Reports and old raw/source files are unchanged.
