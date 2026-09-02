# Source anchors

- `src/gpgpu-sim/dtc-l1-common.h`: whole-line logical Tag -> physical model,
  RR allocator, generation identity, pending/valid behavior, FIFO readiness,
  IO Tag-bank arbitration, and directed counter state.
- `ldst_unit::dtc_l1_io_memory_cycle()` in `src/gpgpu-sim/shader.cc`: consumes
  already-coalesced accesses, groups 128B references, applies IO Tag service,
  and never calls conventional `l1_cache::access()`.
- `ldst_unit::{dtc_l1_io_issue_lower_requests,dtc_l1_io_consume_response}`:
  one request/SM/cycle, immutable request UID lookup (including sector-child
  original root), generation checked completion, and no conventional fill.
- `ldst_unit::dtc_l1_io_writeback_head()`: finite operand-collector writeback,
  FIFO-only retirement, and true instruction completion.
- `gpgpu_sim::shader_print_dtc_l1_stats()` and `deadlock_check()`: drain
  assertions, independent conventional MSHR counters, and compact active-IO
  resource deadlock state.
- `util/dtc_l1/parse_dtc_l1_summary.py`: strict, provenance-bearing PAPER_IO
  parser.
