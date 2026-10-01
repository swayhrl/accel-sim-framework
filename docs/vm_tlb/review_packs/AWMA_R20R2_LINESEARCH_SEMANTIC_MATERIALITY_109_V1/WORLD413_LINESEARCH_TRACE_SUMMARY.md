# World413 line-search predicate, chronological first paired outcomes

The fixed t152 entry was restored byte-for-byte before every complete B1024 solver replay. The observer-ON graph produced 30 clear-bit and one set-bit result in 31 qualified same-graph repeats; no fresh-capture fallback was needed. The chronological first clear (`ON_00`) and first set (`ON_30`) form the reported pair. All 31 raw full outputs, per-outer/inner observer traces, input checks, and checksums are indexed in `RAW_DATA_INDEX.tsv`; the selected pair is in `WORLD413_LINESEARCH_TRACES.json`.

The decisive difference is outer solver iteration 2, inner line-search iteration 1 (zero-based):

| Quantity | Clear bit | Set bit |
| --- | ---: | ---: |
| `gtol_accept` | 0.0112164542 | 0.0112163993 |
| `hi_next.cost` | -4618.8232422 | -4618.8144531 |
| `hi_next.derivative` | +0.00244140625 | -0.01318359375 |
| `abs(hi_next.derivative) < gtol_accept && cost < 0` | true | false |
| `conv_hi` / `ls_done` | true / true | false / false |
| Inner iterations in outer 2 | 2 | 20 |
| Outer-2 selected alpha | 0.5598629117 | 0.5598625541 |
| Outer-2 improvement | 4618.8232422 | 4618.8144531 |

For the clear case, the positive derivative is below the acceptance threshold and the negative cost makes `conv_hi` true; the search accepts and breaks. For the set case, the derivative's magnitude is slightly above the threshold, `conv_hi` is false, bracket-swapping continues, and none of the source's `ls_done` components becomes true by the fixed 20-iteration bound. The kernel still applies its selected alpha to qacc/Ma/Jaref before setting `LS_ITERATIONS`. This is an observed threshold/iteration-limit branch, not a changed solver algorithm or a failed complete solver execution.

The two traces differ slightly already in earlier floating state: at outer 1, alpha is 0.1703611016 versus 0.1703629941. The same frozen input therefore does not imply bitwise-identical reduction history. The targeted source scratch audit finds no specific read-before-write dependency needed to explain this variation; it does not prove all implementation nondeterminism is exhaustively understood. Across all 30 clear-bit observer runs, outer-2 alpha ranged 0.5598613620–0.5598636270 and improvement 4618.7939453–4618.8359375; the set-bit values lie inside both ranges. A clear bit can arise by other line-search termination predicates in other repeats, so the paired `conv_hi` explanation is not claimed for every clear run.

Both paired complete solver results have `nefc=46`, `solver_niter=8`, exact global constraint coverage and non-LS overflow signature. The set-vs-clear world413 final max normalized differences are: qacc `4.60e-7`, qfrc_constraint `6.74e-7`, valid efc.force `3.70e-6`, and efc.Ma `1.03e-6`. These are below the frozen local perworld screen `5.301662e-4`; each run also independently passes the parent B0 floating/global RMS, finite, capacity, done and qfrc source-relation checks. The flag itself differs, preserving the accepted R20R1 exact stop-signature failure.

No timing was performed, and the 20 inner iterations in one line-search invocation are not an active-world performance result.
