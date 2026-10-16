# Lane 1 functional source map

Common parent: Core 1fc248aa / Framework 54fbc786. Coordination 6c136e2a is
only the task authority. Producing commit/binary/config identities are in the
stage receipt, never inferred from the documentation branch tip.

- `ep-l2-ft-interface.h`: common handle/role/reservation/refusal ABI.
- `gpu-cache.h`: configurable pool size, role ownership, pins, explicit reserve/
  release/transfer, generation/sector checks and shared bank arbiter; FT state.
- `gpu-cache.cc`: default-OFF dispatch; real descriptor/lower-read producers;
  baseline issue eligibility/accepted virtual hooks; returned fill validation.
- `ep-l2-ft-cache.inc`: actual l2_cache FT admission, two-stage static copy,
  unified landing/role transition, all L2_WRBK_ACC producer binding, real lower
  handoff/release, independent descriptor response pins and EPL2FTV1 evidence.
- `gpu-sim.cc`: parser registration; FT mode/WBUF defaults zero.
- `mem_fetch.h/.cc`: symbolic sector version carrier after WB bank readout.
- `l2cache.cc`: terminal FT records; unchanged set_done drives WAD retirement.
- `tests/ep_l2/test_ft_wbuf.cc`: production access/issue/fill/commit against
  independently prepared version expectations and adversarial resource pressure.
- `tests/ep_l2/ft_wbuf.config`: reduced geometry directed fixture, not a
  performance configuration; physical payload and WAD capacities remain explicit.
- Framework `tests/ep_l2/ft20261016/*.config`: append-only mode overlays after
  the unchanged calibrated Banked D512 primary hierarchy.

The current qualified target policy remains WRITE_BACK + LAZY_FETCH_ON_READ;
production tests include global reads/writes and incoming L1 writebacks. Broader
allocation-policy coverage must be tested explicitly before claiming it.
