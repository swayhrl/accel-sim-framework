# Reproduce AF CPU qualification

Source anchors and exact per-file hashes are in `SOURCE_SHA256.tsv` / `CORE_FETCH_BACK.json`. Core is `19dafca6b5636ee26f4c35e566c24e17e645edaf`, derived from X2 `e32afdcf44be3374ff36d22568ed01a075459b6f`; use a fresh AF checkout and fresh build directory. Do not mix its object files or library with frozen/other-Lane builds.

`CORE_DELTA.patch` is a zero-context source delta; apply only to the exact base with `git apply --unidiff-zero`. This representation avoids context-only blank lines being mistaken for trailing whitespace when the patch itself is versioned. No production source changed during that packaging correction.

The following are build/CPU-test commands only, with at most2 compiler tasks and serial CTests. They do not run accel-sim, kernels, GPU or native workloads:

```bash
cmake -S "$AF_CORE" -B "$AF_BUILD" \
  -DCMAKE_BUILD_TYPE=Release -DGPGPUSIM_BUILD_DTC_L1_TESTS=ON \
  -DCUDAToolkit_ROOT=/usr/local/cuda-11.8 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build "$AF_BUILD" --parallel 2 --target \
  dtc_l1_reclaimable_victim_fallback_test dtc_l1_reclaimable_victim_option_test \
  dtc_l1_m1_common_test dtc_l1_bad_generation_test \
  dtc_l1_completion_accounting_test dtc_l1_finite_service_test \
  dtc_l1_source_invalidation_test dtc_l1_source_invalidation_integration_test \
  dtc_l1_k0_equivalence_test
ctest --test-dir "$AF_BUILD" --parallel 1 --output-on-failure
```

The parser CTest pins `LD_LIBRARY_PATH` to its own Core target. Production assertions remain enabled in the project's Release recipe. Deliberate stale-generation/duplicate-completion negative child tests must SIGABRT, with parent success; core dumps are disabled by the new test.

Framework `scripts/default_off_probe.cc` builds once against the fixed X2 common-header blob and once against AF, with no flag set. It executes four deterministic header API sequences (finite/nonfinite×K0/K1) and compares524 output lines byte-for-byte. `scripts/renamed_pool_witness.cc` checks the natural hidden-owner opportunity with physical3>Tag2, and reports current C++ ABI sizes; compile its `AF_BASELINE_SIZES` variant against X2 for the size comparison. These are bounded synthetic traces, not accepted workload cycles.

`scripts/collect_cpu_evidence.py` only summarizes AF-owned CPU files and verifies source identity; it never starts tests or simulator processes. Its absolute paths describe this original174 publication environment. Raw CPU stdout/stderr/XML, binaries and build trees remain under `/workspace/dtc-lane-af-victim-fallback-174-v1/cpu` and `/workspace/builds/dtc-lane-af-cpu-174-v1`; the Git package keeps small parsed receipts and their SHA only.
