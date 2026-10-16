# Changed files

Scope: util/dtc_l1/native_coverage_109_v1, dedicated review pack and branch-local docs/dtc_l1/codex_handoff/LATEST_REPORT.md only. No simulator/Core/config, frozen payload or other-project worktree changes.

 docs/dtc_l1/codex_handoff/LATEST_REPORT.md         | 2499 +---------------
 .../BINARY_FRAMEWORK_INPUT_IDENTITY.json           |   50 +
 .../GPU_LOCK_RECEIPT.json                          |    9 +
 .../LayerNorm_1024_ncu_sass_txt_FORMS.json         |   18 +
 .../DTC_NATIVE_COVERAGE_109_V1/NATIVE_FINDINGS.md  |   27 +
 .../ORDERED_OPERATOR_KERNELS.json                  |   71 +
 .../PREREGISTRATION.json                           |   10 +
 .../DTC_NATIVE_COVERAGE_109_V1/PROFILE_METRICS.tsv |   16 +
 .../DTC_NATIVE_COVERAGE_109_V1/R0_FIXED_COHORT.tsv |   13 +
 .../DTC_NATIVE_COVERAGE_109_V1/R0_SUMMARY.json     |    9 +
 .../DTC_NATIVE_COVERAGE_109_V1/README.md           |   41 +
 .../SPMV_SOURCE_INPUT_IDENTITY.json                |   42 +
 .../DTC_NATIVE_COVERAGE_109_V1/TIMING_SAMPLES.json | 3082 ++++++++++++++++++++
 .../DTC_NATIVE_COVERAGE_109_V1/TIMING_SUMMARY.tsv  |   16 +
 .../diagnostic_sass_FORMS.json                     |   11 +
 .../spmv_sass_FORMS.json                           |   13 +
 util/dtc_l1/native_coverage_109_v1/analyze.py      |   39 +
 util/dtc_l1/native_coverage_109_v1/campaign.py     |   63 +
 util/dtc_l1/native_coverage_109_v1/capture.py      |   46 +
 util/dtc_l1/native_coverage_109_v1/check_spmv.py   |   12 +
 util/dtc_l1/native_coverage_109_v1/diagnostic.cu   |   62 +
 util/dtc_l1/native_coverage_109_v1/inventory.py    |   16 +
 util/dtc_l1/native_coverage_109_v1/layernorm.py    |   19 +
 util/dtc_l1/native_coverage_109_v1/prepare_spmv.py |   27 +
 24 files changed, 3720 insertions(+), 2491 deletions(-)
