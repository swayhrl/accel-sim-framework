# C13 per-arm conservation audit

Every admitted row below was independently re-parsed from its immutable C13 raw log. `gpu_sim_cycle` occurs exactly once per marker and its sum equals both raw full-ROI total and runner validation total. The accepted Operator-aware parser also rechecks monotonic snapshots and delta-to-terminal closure for active attribution `vm_*` fields.

| arm | ROI | markers | per-kernel cycle sum | full ROI total | active `vm_*` fields | result |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| C13-CAP-P320 | prefill | 692 | 62377411 | 62377411 | 285 | PASS |
| C13-CAP-P768S10 | prefill | 692 | 62058600 | 62058600 | 285 | PASS |
| C13-LAT-D11 | decode1 | 740 | 34539934 | 34539934 | 285 | PASS |
| C13-LAT-P8 | prefill | 692 | 59939210 | 59939210 | 285 | PASS |
| C13-LAT-P9 | prefill | 692 | 60906959 | 60906959 | 285 | PASS |
| C13-SEL-D10 | decode1 | 740 | 34470902 | 34470902 | 285 | PASS |
| C13-SEL-D10-CTRL-NEWBIN | decode1 | 740 | 34432059 | 34432059 | 285 | PASS |
| C13-SEL-P10 | prefill | 692 | 62202481 | 62202481 | 285 | PASS |
| C13-SEL-P10-CTRL-NEWBIN | prefill | 692 | 62058600 | 62058600 | 285 | PASS |
