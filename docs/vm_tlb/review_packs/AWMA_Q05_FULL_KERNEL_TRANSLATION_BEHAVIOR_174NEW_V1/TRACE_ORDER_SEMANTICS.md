# Trace-order semantics

The simulator-native trace is a complete selected-kernel CTA/warp/instruction stream. Its file order supports structural first/last and reuse summaries. This stage has not proven a global cross-CTA file-record order equivalent to execution cycle time; all offline ordering metrics are therefore `STRUCTURAL_TRACE_ORDER_ONLY`.