# Directed Line-MSHR boundary tests

Command:

```text
bash /workspace/worktrees/gpgpu-sim-ep-l2-mshr-causality/tests/ep_l2/run_descriptor_mshr.sh
```

Result: `EP-L2 C3 descriptor/MSHR directed tests: PASS`.

The Lane-E addition constructs `mshr_table(256, 1, 1024, 32)` with distinct
128-B lines and exercises 127, 128, 129, 255, and 256 live entries. The next
distinct line reports exactly `EP_L2_BLOCK_LINE_MSHR_FULL`; descriptor capacity
and the per-address cap cannot be first. It releases one ready entry, admits a
new line, then drains every entry and verifies zero Line-MSHR and descriptor
ownership. Natural D512/M256 convolution additionally reports Line-MSHR
`p95=135`, `max=158`, proving the telemetry path above 128 is not clipped.
