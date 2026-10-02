# Online signal availability

The exact accepted path is in `full_generation.py`, `reference.py`, and
`heads.py` from scientific parent `69e74fe...`. XGrammar 0.2.8 allocates and
fills an `int32` CPU bitmask. At B4 and vocabulary 151,936 this is
`4 * ceil(151936/32) * 4 = 75,968` bytes.

In the live generation loop, CPU mask work is submitted concurrently with the
GPU backbone. `future.result()` returns before `head_start`; therefore its CPU
mask and legal-ID outputs exist before head timing begins. Importantly,
`fill_masks` stops its `grammar_fill_ms` timer immediately after matcher fill,
then performs full-mask unpacking and `np.flatnonzero` legal-ID materialization.
That materialization is before the head but is not part of the reported matcher
fill duration.

`HeadArms.select` does not accept those upstream legal IDs. Its `_base` method
unpacks the full CPU mask and materializes the IDs again inside every accepted
A0/A3 head-region measurement. This duplicate work is already charged to both
arms and must not be charged a second time in the retrospective accounting.

| Signal | Earliest exact availability | Residency | Extra full-mask scan? | D2H sync? | Accepted-path status |
|---|---|---|---|---|---|
| Active/done rows | Before mask generation | CPU | No | No | Already available |
| XGrammar bitmask | After matcher fill, before `future.result()` returns | CPU | No | No | Already available; mask fill itself is outside head timing |
| Exact legal IDs | After CPU bitmask unpack plus `flatnonzero`, before head | CPU NumPy int32 lists | Yes, performed by `fill_masks`; current head then repeats it | No | Materialized upstream but not passed into `HeadArms.select` |
| Legal count | When each legal-ID list length is known | CPU scalar | No beyond legal-ID materialization | No | Available upstream; recomputed inside timed `_base` |
| Singleton status | When legal count is known | CPU boolean | No beyond legal-ID materialization | No | Available upstream; singleton bypass is included in A0/A3 timings |
| Union size/fraction | Not computed before head in live R81 | CPU if implemented | New union/unique over IDs, or new mask OR/popcount | No | `UNKNOWN/NONFREE`; accepted ledger computes union after head |
| Identical-mask group identity | Inside A3 after arm selection | CPU dictionary keyed by mask bytes | No additional unpack, but scans mask bytes | No | Included only in A3 head timing; not available to RULE_U01 beforehand |

RULE_U01 can avoid a new full-mask unpack only if a future runner reuses the
upstream legal-ID lists. It still needs a new exact union-size computation and
must measure it. Reading `legal_union_count` from the accepted ledger would use
post-head/future information and is not deployable.

No dispatch signal here requires device-to-host transfer because the source
mask and IDs are already on CPU. A3 itself subsequently pays legal-ID and row
metadata H2D costs inside its accepted timing.
