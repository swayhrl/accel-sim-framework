# Source anchors

- `src/gpgpu-sim/dtc-l1-common.h`: `oo_frontend` and
  `sector_oo_frontend`; line-level Ref Count, slot generation, sector state,
  waiters, shadow checks and reclamation.
- `src/gpgpu-sim/shader.cc`: OO/sector admission, lower request construction,
  root-or-child response routing, writeback, mode-specific statistics and
  exact Paper Base activation.
- `src/gpgpu-sim/shader.h`: sector front-end ownership and lower inflight
  expected-sector identity.
- `src/gpgpu-sim/l2cache.cc`: source-backed 32B single-sector request rule in
  `memory_sub_partition::breakdown_request_to_sector_requests`.
- `tests/dtc_l1_m1_common_test.cc`: O01–O12, S01–S09 and causal HOL tests.
- `tests/dtc_l1_bad_generation_test.cc`: O13 `SIGABRT` negative test.
- `util/dtc_l1/parse_dtc_l1_summary.py`: strict OO/sector metric/provenance
  parser.
