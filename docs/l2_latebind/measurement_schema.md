# LateBind-L2 measurement schema

## Model boundaries

All timestamps use the global GPGPU-Sim cycle supplied to the L2 cache.

| Metric | Start | End |
| --- | --- | --- |
| L2 request latency | input request accepted by `l2_cache::access` | reply enqueued to the subpartition L2-to-interconnect queue |
| reservation lifetime | baseline tag sector enters `RESERVED` after an accepted miss | that sector is filled and becomes readable |
| MSHR residency | new MSHR entry inserted | its last merged response leaves the MSHR |
| writeback residency | dirty victim creates the writeback request | request is accepted by the lower-memory port |
| resident payload occupancy | sample after `l2_cache::cycle` | count valid or modified sectors only |
| transient metadata occupancy | sample after `l2_cache::cycle` | count each live oracle record once |

The baseline's input gate (`m_L2_dram_queue` and output queue availability) is
reported separately from cache-internal rejection.  It is not folded into
reservation failures or MSHR-full failures.

## Histograms and units

- Latency and lifetime histograms use exact cycles through 255 and power-of-two
  buckets thereafter.
- Occupancy is reported as both integral sector-cycles/record-cycles and
  maximum simultaneous occupancy.
- Dirty traffic is reported as bytes, sectors, and writeback requests.
- All counters have per-subpartition rows plus an aggregate row; aggregates
  are sums except `max`, which is the maximum of subpartition maxima.

## Stats-off equivalence gate

For each directed trace, `stats=off` is compared with frozen baseline by:

1. exit status;
2. complete stdout metric stream after removing provenance paths and wall-clock
   fields;
3. emitted request/fill/reply event digest; and
4. total simulation cycles and instructions.

An oracle mode is never allowed in this gate.  The gate protects baseline
instrumentation, not the counterfactual behavior of an oracle.
