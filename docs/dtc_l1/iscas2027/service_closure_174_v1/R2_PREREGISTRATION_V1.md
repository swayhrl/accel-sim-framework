# R2 paired evidence preregistration V1

Fixed pilot: BICG, Btree, 2DConvolution, Hotspot1, complete original instruction scope. Retain the complete twelve-workload cohort after row-local pilot qualification, including ATAX, GESUMMV and regressions. Do not wait for a slow pilot batch to finish before starting independent qualified rows. Do not compute GM12 until all twelve valid rows for a comparison exist.

Primary new-model arms: IO PIB256 and OO PIB128, logical 16KiB/128B/4-way and dedicated physical80KiB, finite service ON, common global lower credit cap32768. This cap is fixed now, before the new comparative outcomes; it does not enlarge any per-SM candidate queue or remove ICNT backpressure. It accommodates the retained historical row-local cap distinctions without relabelling old data as new-model output.

Comparison roles remain distinct:

| Arm | Conventional data | PIB | L1 MSHR | Role |
| --- | --- | --- | --- | --- |
| B16-N | 16KiB,32 sets×4 ways | 8 | 32 | matched128B structural baseline, exact canonical row reuse |
| TC80-N | 80KiB,32×20 | 8 | 32 | conventional searchable-capacity control, exact canonical row reuse |
| WAIT128 | 16KiB,32×4 | 128 | 32 | waiting-depth-only diagnostic on the four pilot workloads |
| TRAD96-P256-M512 | 96KiB,32×24 | 256 | 512 | the single resource-enhanced traditional design |

The enhanced traditional design is selected from source resource counts: DTC currently retains a conventional16KiB side path as well as its dedicated80KiB array, and its side-path config parses512 MSHRs. Give the enhanced conventional design96KiB,512 MSHRs and PIB256 rather than hide these resources or give it free extra ports. Use the same four conventional cache banks,32B bank data width,20-cycle latency setting and merge8; existing finite conventional ports/backpressure remain. The96KiB geometry needs unified-size96 and is source legal by the same arbitrary-associativity construction used for TC80. No additional port mechanism is introduced.

Cost method is a declared **resource vector**, not fitted silicon area: report data bytes, searchable entries/ways, PIB records, MSHR records, maximum merge records, Tag/data/refill/metadata-update ports and delays, plus DTC physical/line-reference/waiter state and conventional side-path state. Host C++ object sizes and pointers are not hardware-area estimates. DTC's32-lane last-reference update fabric and four waiter-update ports are charged as explicit assumptions. Total metadata bits, CAM implementation and synthesized area remain unresolved; neither equal area nor original-platform4.7% OO/IO area transfers to these designs.

Mechanism control C: IO128 versus the primary OO128, finite service identical, only the four pilot workloads. Reuse the primary OO128 row; launch only the necessary extra IO128 row. Require full admission, separate collection/writeback waits, map-loss-to-free statistics and occupancy integrals. Do not reinterpret old frontend-ready counters.

New comparative rows use Core `78947aa2e4e8197e14d97d5989109865c6669216`. Conventional arms use canonical Core `6582b9d171330d88b17e8d5294c97704229e3823` and its exact frozen binary, supported by R1's unchanged BASE/OFF execution check and guarded source diff. Preserve those distinct identities. Any baseline reused at its original lower cap keeps that exact identity; require zero lower-cap stalls and sufficient peak headroom before claiming its execution equivalence to an unbinding larger cap. No old IO/OO timing row is reused as finite-service performance.

Modern baseline-only counterfactual remains a separate scope. New native SpMV/LayerNorm receipts require immutable109 source/binary/input/trace identity before admission. Missing receipts do not trigger polling or invented substitutes. RTX3070 remains conditional and is not scheduled here.
