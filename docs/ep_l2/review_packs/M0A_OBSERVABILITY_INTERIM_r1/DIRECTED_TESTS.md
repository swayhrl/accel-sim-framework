# Directed and parser tests

* Core Release CMake build: PASS.
* Framework Release CMake build linked to frozen Core candidate: PASS.
* `python3 -m unittest util/ep_l2/tests/test_parse_epl2_m0a.py`: PASS (2
  tests): complete 64-slice stream accepted; incomplete stream fails closed.
* Static switch audit: all `ep_l2_m0a_stats` reads are in M0a telemetry,
  boundary, or printing guards; no admission/arbitration source consumes it.
* Natural OFF/ON controls: all three completed controls have equal terminal
  cycles and instructions. Final analyzer will also compare parsed B0/L1/DRAM
  records and terminal invariants after live `scan` completes.

No retry event is relabeled as an opportunity: observations occur on the
current exact frontend head once per cycle, before any commit; a held head is
therefore observed once per held cycle.
