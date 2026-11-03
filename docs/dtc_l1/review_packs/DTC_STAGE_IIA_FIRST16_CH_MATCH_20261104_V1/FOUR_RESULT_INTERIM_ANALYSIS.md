# Four-result interim CH matching analysis

Four of the16 authorized CH identities have accepted strict/archive/native-restore results. The common F128/F256 set contains only convolutionSeparable and vectorAdd (n=2/8), so these are not whole-first8 or core32/35 conclusions. The remaining12 CH outcomes retain their fixed input/configuration slots. Performance regressions are valid accepted observations and are distinct from archived failed experiments.

Performance below is own P0 cycles / variant cycles; P0 is1 and values above1 are faster.

| Program | Design | P0 | F128 | F256 |
|---|---|---:|---:|---:|
| convolutionSeparable | CH |1|1.173857|1.370455|
| convolutionSeparable | DH |1|1.187151|1.422263|
| vectorAdd | CH |1|1.029370|0.990059|
| vectorAdd | DH |1|1.019957|0.919938|

convolutionSeparable CH-F128 is702940cycles and CH-F256602100cycles; the matching original DH values are674364 and562886. For vectorAdd the new CH values are214503 and223020; original DH values are213053 and236217. Whole raw cycle and identity sources are in the independent paired table and accepted-result receipts.

On the current two-program common set, F128's extra relative DH gain is approximately1.001x and F256's approximately0.982x. This limited sample illustrates why larger DH own speedups alone do not establish a larger relative DTC advantage after CH matching. It does not select a uniform configuration for the full suite, nor justify selecting different F values per program.

Figures preserve both negative vectorAdd F256 responses and all pending cells. Runtime resource summaries remain periodic observations. The source-bound counter audit's mixed-scope and latency-window limitations continue to apply. L1 mechanism/area differences remain; FR-FCFS capacity and shared credits change together. No new scientific budget, simulator, trace, combination or remaining48 execution batch is created by this report. The Englishv0.23 manuscript is unchanged.
