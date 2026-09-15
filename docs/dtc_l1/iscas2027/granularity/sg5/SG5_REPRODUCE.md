# SG5 design-gate reproduction

```sh
python3 util/dtc_l1/validate_sg5_design.py \
  --core-repo /workspace/repos/gpgpu-sim_distribution

python3 util/dtc_l1/validate_sg5_implementation.py \
  --observer-core /workspace/worktrees/gpgpu-sim-iscas2027-sg5-observer
```

The dedicated Core also supplies an exact source-directed fixture for the
production storage-only counter primitive:

```sh
cmake -S /workspace/worktrees/gpgpu-sim-iscas2027-sg5-observer \
  -B /tmp/dtc-sg5-unit-afe978ea \
  -DGPGPUSIM_BUILD_DTC_L1_TESTS=ON -DGPGPUSIM_ENABLE_TRACE=OFF \
  -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/dtc-sg5-unit-afe978ea \
  --target dtc_l1_lower_traffic_observer_test --parallel 2
ctest --test-dir /tmp/dtc-sg5-unit-afe978ea \
  -R '^dtc_l1_lower_traffic_observer_test$' --output-on-failure
```

It proves `sector32`, `normal128`, `dtc_io128`, pending-hit +0,
duplicate-after-eviction +128B, and the observer create-side count together
with exact-once terminal completion. It does not launch `accel-sim.out` and
is not a trace-driven equivalence or G6 row. NN/Btree OFF/ON equivalence and
G6 remain independently gated. The observer Core descendant is `fa9a6bdb` on
`hrl/iscas2027-dtc-sg5-lower-traffic-v0`; no frozen Core/runtime is touched.
