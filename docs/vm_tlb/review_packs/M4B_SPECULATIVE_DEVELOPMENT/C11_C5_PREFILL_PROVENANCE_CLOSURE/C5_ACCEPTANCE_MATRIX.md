# C5 execution acceptance contract (frozen, not executed by C11)

每一个 command point 必须先通过 C11 的 input validator，并在 run root 写入输入
SHA256 manifest；所有值必须等于 `C5_ARM_MATRIX.tsv` 与
`C5_COMMAND_MANIFEST.tsv`。不满足任何一项时，该点为 `INVALID_INPUT`，不是
性能样本。

| Area | Required pass condition |
| --- | --- |
| Identity | Framework/Core/binary/config/trace-list/V2 registration/object-map hashes all match the frozen manifest. |
| Trace | Exact full compute-only list; source list hash is prefill `a40…6e6f` or decode1 `b6c…d0dc`; no trim/reorder; every symlink resolves inside the recorded immutable root. |
| Common PA | A registered full Weight page resolves to the recorded nonidentity PPN through ordinary PTE in F0/F1/F2/F5/F9 and through Segment in F7/F8. The tail 4KiB remains conventional. |
| F0/F1/F2/F5/F9 | Segment inactive: no Segment lookup/hit/suppression or bypass. V2 registration remains the ordinary PA backend. F5 must report physical PWC 120 entries, 40/40/40, 4-way, E656. |
| F7/F8 | 35 local replicas, N=8, Lseg exactly 5/10/20. A read descriptor hit must suppress L2/MSHR/PWQ/walker/PWC/PTE and conventional TLB fill; write/atomic/boundary/ASID/epoch failures fall back conventionally. |
| Ordering | HIT_FIRST / MISS_JOIN counters must conserve; L1-hit does not wait for a slower Segment, a Segment hit suppresses late conventional work, both miss launches exactly one lower translation, retry never re-probes. |
| PTE/queues | PTE memory access remains physical/nonrecursive; walker/PWQ/MSHR limits hold; no undrained request at termination. |
| Cross-layer telemetry | Segment, conventional VM, requester wait, PTE wait, L1D, L2, queue and DRAM records are emitted and parser-valid. Lower-path pressure must be reported rather than hidden by a numerator change. |
| Exact once | completed/requester/waiter/MHSR/PTE and object-attribution conservation equations hold; no duplicate data/store/atomic effect. |
| Fairness | Only primary F0/F1/F2/F5/F7/F8/F9 are equal-cost matrix members. F1/F8 retain `REFERENCE_APPROX_SUBENTRY_16`; F7/F8 retain `SPECULATIVE_CANDIDATE`. H0 is rejected. |

F6 may be assessed only after a separately approved 2MiB driver allocation/page-map policy can
provide the same PA mapping. It must be labelled `DIAGNOSTIC_NOT_EQUAL_COST_PRIMARY`; it is not an
incomplete row in this C11 primary matrix.

任何 C5 performance result 都需要单独的 execution authorization；本 acceptance contract
不构成该授权。
