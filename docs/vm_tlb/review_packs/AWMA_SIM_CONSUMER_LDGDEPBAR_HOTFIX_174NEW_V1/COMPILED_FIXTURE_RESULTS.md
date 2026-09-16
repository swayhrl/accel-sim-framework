# Compiled strict-validator fixture results

The following cases ran through the real compiled `traceg_grammar_smoke` binary, not helper-only logic.

| Case | Result |
| --- | --- |
| `LDGDEPBAR`, width 0, no address | PASS |
| `LDG.E.32`, width 0 | FAIL: zero/missing width |
| `LDGSTS`, width 0 | FAIL: zero/missing width |
| Existing valid `LDG.E.32`/`STG.E.32` memory record | PASS |
| Existing malformed width test and missing-address test | FAIL |

All five compiled-fixture unittest cases passed. The full suite result is recorded in `FULL_UNITTEST_RESULTS.txt`.