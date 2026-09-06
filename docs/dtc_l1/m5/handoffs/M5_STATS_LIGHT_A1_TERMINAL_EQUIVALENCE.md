# M5 statistics-light A1 terminal equivalence

Status: **TERMINAL_EQUIVALENCE_PASS; INDEPENDENT_SAME_PLACEMENT_PASS;
A1_ADOPTED_FOR_FUTURE_UNLAUNCHED_FORMAL_TRIPLETS**.

This is a host-observer audit only.  It changes neither the Core mechanism nor
the trace, cache, memory, DTC, parser, or formal-result identity of any row.

## Fixed evidence and terminal status

All rows use the immutable BICG bundle
`ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`,
the frozen 80-SM/cap-10240/ratio-zero model, natural termination (exit status
zero), empty stderr, and no assertion/fatal/output-mismatch/unclassified
deadlock signature.  A1 adds only
`-gpgpu_runtime_stat 500000`; its overlay SHA-256 is
`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.

| mode | identity | A0 wall s / CSV bytes | A1 wall s / CSV bytes | A1 rate gain | strict parser | parser-visible scientific equivalence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| PAPER_BASE | pre-repair controlled observer pair; Core `12097864...` | 19,482 / 216,717,458 | 18,860 / 243,633 | 1.0330x | PASS / PASS | PASS |
| PAPER_IO | repaired Core `15cfa76e...`, Framework `dc7836c4...` | 6,630 / 29,944,084 | 4,849 / 56,729 | 1.3673x | PASS / PASS | PASS |
| PAPER_OO | repaired Core `15cfa76e...`, Framework `dc7836c4...` | 6,123 / 30,215,803 | 4,789 / 56,932 | 1.2786x | PASS / PASS | PASS |

The strict parser compared final cycles/instructions; all DTC
new-miss/pending-hit/valid-hit, PIB, lower create/issue/response and
acquire/release/current fields; dependency counts; inflight/ref final state;
the parser-visible L1/L2/traffic fields; and every other parser-consumed M5
scientific field.  There were zero differences in each pair.  The only raw
final-report differences were host-time/rate fields and rounded generic
latency-report values (`averagemflatency` and/or interconnect averages), which
are observer reports outside the M5 parser/formal metric contract.

The repaired IO/OO A0 and A1 outputs respectively close all IO/OO
PIB/inflight/lower/dependency/ref accounting to zero/balanced values.  The
Base pair closes Base PIB and lower accounting likewise.  Compact local
evidence is retained in the existing isolated namespaces; raw logs and CSVs
are intentionally not committed.

## Independent same-placement confirmation and adoption

The required independent confirmation ran after the table above on CPU 46,
with repaired Core `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, runtime binary
SHA-256 `3e71cb73e7769be43fc4e7c95c59dba6d50540e3827a38a46e4016cb2877dc27`,
the same immutable BICG bundle, `PAPER_IO` base config SHA-256
`7acb491414f84f9738f6bbc76b0bc2bc83dd146fd205e6f8636126b135599f5c`, and
the A1 observer overlay SHA-256
`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.
There is no architecture, cache, memory, DTC, trace, payload, or source-input
difference between the two runs.

| same-placement row | A0 | A1 | result |
| --- | ---: | ---: | --- |
| natural exit status | 0 | 0 | PASS |
| wall seconds | 2,683.85 | 2,666.21 | A1 `1.0066x` faster |
| simulated cycles / instructions | 9,324,397 / 158,601,216 | 9,324,397 / 158,601,216 | exact |
| all 62 strict parser-visible metrics | reference | reference | exact; zero differing fields |
| IO lower create / issue / response | 17,823,985 / 17,823,985 / 17,823,985 | same | balanced |
| completion dependencies closed / count | 18,350,080 / 18,350,080 | same | balanced |
| final IO PIB / inflight / lower outstanding | 0 / 0 / 0 | 0 / 0 / 0 | drained |
| compressed runtime CSV bytes | 29,949,952 | 61,440 | A1 reduced by 99.79% |

The sole `deadlock` text is the echoed enabled configuration option; both
stderr files record exit zero and neither has assertion, fatal, output-mismatch
or unclassified-deadlock evidence. This closes the final adoption condition.

**Frozen adoption boundary.** A1 means exactly the base formal configuration
plus `-gpgpu_runtime_stat 500000` from the overlay hash above. It is now the
observer identity for **future, not-yet-launched** Paper and Extended formal
Base/IO/OO triplets. Existing valid A0 or pre-adoption candidates remain under
their recorded identity, are neither rerun nor relabelled, and a future triplet
must use one common observer identity across all three modes. This adoption is
host-observer-only and has no scientific-result invalidation scope because the
independent terminal comparison proved parser-visible equivalence.
