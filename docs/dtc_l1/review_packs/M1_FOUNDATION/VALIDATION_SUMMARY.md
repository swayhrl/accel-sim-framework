# M1 HARD-gate validation summary

| Gate | Evidence | Result |
| --- | --- | --- |
| M1.0 source audit | `implementation/SOURCE_INTEGRATION_MAP.md`; active Core `48b0be73`, Framework `ff26ef46` | PASS |
| B01A-E | `/tmp/dtc-l1-core-build`: `dtc_l1_m1_common_test` exact 1/2/4/32-line and sector-mask cases | PASS |
| B02/B03 | same CTest: depth-2 admission, release only at modeled completion, drain invariant | PASS |
| B04/B05 | same CTest: same-bank serial; four distinct logical banks concurrent; per-bank/total caps | PASS |
| B06 | Paper Base VecAdd, MSHR=1: 26,265 entry-full; PIB 24/24/0 | PASS |
| B07/R07.1-R07.6 | `A:1:1` merge stress: 166 merge-full; PIB 33/33/0; clean baseline also 166 | PASS |
| B08 | Paper Base VecAdd, cap=2: peak=2, cap-full=13,091, acquire/release=64/64 | PASS |
| B09 + LEGACY neutrality | clean/current exact equality for hit, merge, bypass, and VecAdd on instruction/cycle/L1/L2/DRAM fields | PASS |
| Counter/parser closeout | primary B06: 9,029+72+0=9,101; B08: 3,970+72+13,091=17,133; independent MSHR/resource fields parse under `--strict` | PASS |
| hygiene | release build + CTest PASS; `git diff --check` and worktrees clean at closeout | PASS |

The primary domain is explicitly documented in `COUNTER_OUTPUT_MAP.md`; the
conventional L1D MSHR retries occur after Paper Base admission/Tag timing and
are independently emitted, not double-charged as a frontend primary reason.
