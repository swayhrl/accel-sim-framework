# C4 builder state at C3 publication

Snapshot time: `2026-09-08T00:22:10Z`.

| Component | State |
| --- | --- |
| v3 non-locality input layer | `COMPLETE`: frozen eight-arm summary and eight structured-export roots are present. |
| v6 prefill locality supervisor | `RUNNING`: PID `651573`; active bounded analyzer child `681375`; highest durable prefill index at the snapshot was `204` of `691` (zero-based). |
| Host PSI gate | `PASS_AT_SNAPSHOT`: memory `full avg10=0.00`, `avg60=0.00`. |
| Locality analysis | `RUNNING / NOT_YET_PASS`; it remains independently host-PSI-gated. |

This is a status record only. `C3_FINAL_STATUS=TERMINAL_PASS` neither waits
for nor certifies the v6 locality result or host PSI suitability for B/C work.
