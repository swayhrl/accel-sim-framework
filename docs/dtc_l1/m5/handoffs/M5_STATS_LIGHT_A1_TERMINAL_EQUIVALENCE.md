# M5 statistics-light A1 terminal equivalence

Status: **TERMINAL_EQUIVALENCE_PASS; A1_NOT_YET_ADOPTED**.

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

## Adoption disposition

A1 is materially faster for repaired IO and OO and reduces the compressed
runtime CSV by more than 99.8% in every measured pair.  It is nevertheless
**not yet the formal default**.  The existing audit acceptance rule requires
one independent same-placement A0-versus-best-A1 confirmation before A1 may
be proposed for future formal rows.  Existing completed formal candidates
remain reusable only under their recorded observer identity; none is rerun or
relabelled because of this host-cost result.

The next bounded action is that controlled confirmation.  It must again use
the same Core/runtime, immutable BICG trace, frozen platform/config, natural
terminal/drain requirement, strict parser, and full parser-visible comparison.
Only after it passes may an adoption review freeze the observer-only config
SHA and authorize A1 for unfinished future formal rows.
