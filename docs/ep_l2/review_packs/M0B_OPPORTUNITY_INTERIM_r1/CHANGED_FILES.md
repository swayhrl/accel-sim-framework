# Changed Files

Core candidate changes:

- `src/gpgpu-sim/gpu-cache.h` — default-OFF M0b switch, observation state,
  epoch-safe MSHR sidecar declarations.
- `src/gpgpu-sim/gpu-cache.cc` — allocation/fill/WAD observations and
  `EPL2M0BV1` output; no controller predicate reads M0b state.
- `src/gpgpu-sim/gpu-sim.cc` — option registration only.
- `src/gpgpu-sim/l2cache.cc` — actual lower-issue observation handoff and
  output dispatch only.

Framework candidate changes:

- `tests/ep_l2/m0b_{off,on}.config` — two observation overlays.
- `util/ep_l2/run_m0b_opportunity.py` — provenance-carrying isolated runner.
- `util/ep_l2/parse_epl2_m0b.py` — fail-closed cardinality/semantic parser.

No functional mechanism source was added.
