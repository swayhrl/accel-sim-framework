# Authorized AC source delta

Immutable baseline e32afdcf44be3374ff36d22568ed01a075459b6f has the direct parent
c0a5e2c31e407c57e3a4af3ce529c921e8059a05. Both were fetched by exact SHA into
AC-owned readback refs before creating the new worktrees. Initial AC Core HEAD
was e32; initial AC Framework HEAD was631eb6418f6e7f1f548afd33351cbc0d98d27145.
Final Core is83aca449135703c176cfab29ae43e1245d00a557.

Seven changed paths are allowlisted, with exact hashes/blob IDs in SOURCE_DELTA.json:

- `src/gpgpu-sim/dtc-l1-collect-wb.h`: bounded two-bank timing/ownership state,
  capacity/port/owner assertions and cumulative telemetry.
- `src/gpgpu-sim/shader.cc`: ON-only collector/WB-slot selection, existing success-
  retirement hooks, mode/constructor guard, independent post-arbitration collection,
  ON-only normal statistics delegates. Original sidecar selector priority remains.
- `src/gpgpu-sim/shader.h`: one bool, stage metadata, helper/const print declarations.
- `src/gpgpu-sim/gpu-sim.cc`: independent OPT_BOOL default0 registration only.
- `CMakeLists.txt`: two new CPU test targets/one new CTest, test-only private access.
- `tests/dtc_l1_collect_wb_pipeline_probe.cc`: actual LDST/RFU/normal printer fixture.
- `tests/dtc_l1_collect_wb_resource_test.cc`: full finite bank bound/assert negatives.

Exact removal recovers the baseline whole shader implementation/header, parser
and build wiring. All other tracked paths are byte-identical, including
`dtc-l1-common.h`, `dtc-l1-invalidation.h`, cache/DRAM/abstract hardware code and all
original tests. Existing source invalidation observers/events/normal export are
not reimplemented. The original fully-ready observation loop is untouched.
Collection uses the same service_entry method and quota; the strict `>` WB delay
is retained. No new quota, request/sector effect, trace, frequency, clock, Tag,
physical, PIB or lower-cap setting is introduced by production code.

SOURCE_DELTA.patch is a zero-context patch of the complete Core difference;
review/apply with `git apply --unidiff-zero`. Its reverse check against the new
Core is verified without mutating the worktree. SHA256SUMS binds the review pack;
SOURCE_SHA256.tsv binds1297 baseline/new source and qualification-tool files.
Behavior changes apply only to the explicitly enabled new pipeline. The new
conservative data banks are a separately charged resource, not extra cache
lookup capacity or a change to the original physical pool.
