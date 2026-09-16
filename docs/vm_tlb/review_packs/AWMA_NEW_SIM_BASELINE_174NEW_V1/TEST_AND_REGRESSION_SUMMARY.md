# Tests

Foundation Python regression passed, including rejection when `sync_control` is
omitted. VM-disabled and VM-enabled configuration parsing passed. The recovered
formal Prefill and Decode compute lists passed real trace parsing and bounded
replay on the exact historical source pair. Both reached 10,000 cycles with
nonzero telemetry. No C12 run was repeated for this control-plane repair.
