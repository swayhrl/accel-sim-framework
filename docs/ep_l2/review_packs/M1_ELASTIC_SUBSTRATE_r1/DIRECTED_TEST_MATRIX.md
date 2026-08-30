# Directed test matrix

| Test | Coverage | Result |
|---|---|---|
| `run_payload_store.sh` | static resident/bypass ranges; handle liveness; bypass release/reuse; ownership | PASS |
| `run_payload_banked.sh` | idle immediate grant; same-bank replay; oldest-ready ordering; 4-bank mapping | PASS |
| `run_c3_c7_closeout.sh` | existing descriptor/MSHR, WAD, payload, schema and integrated paths | PASS |
| `run_descriptor_mshr_integrated.sh` | reserve/lower/fill/sector/lazy-write/terminal sidecar consistency | PASS |
| `run_m1_mode_switch.sh` | unsupported future feature parser value fails closed | PASS |
| `test_payload_sector_lifetime.cc` | pending sector, stale generation predicate, replacement ownership | PASS |
| `git diff --check` | whitespace/source integrity | PASS |

The WAD regression exercises failed-admission rollback under the existing
production path; the integrated regression asserts the sidecar after pending
lower issue and after drain.  Existing stale-generation checks ensure a fill
must match the current owner/generation before mutation.
