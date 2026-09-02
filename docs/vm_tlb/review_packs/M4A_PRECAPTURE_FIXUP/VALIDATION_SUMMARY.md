# Validation summary

| Check | Result |
|---|---|
| `py_compile` all package Python files | PASS |
| static contiguous-layout self-test | PASS |
| metadata self-test, including weight-layout offsets | PASS |
| TP4 workload self-test, including produced sidecar fields | PASS |
| shell syntax for capture/rank wrappers | PASS |
| Route-E wrapper rejects missing 4-GPU contract | PASS |
| M4A-C guard rejects unauthorized execution | PASS |
| GPU execution/formal trace | intentionally not run |

No GPU was accessed and no dependency/model download was performed.
