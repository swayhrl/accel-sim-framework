# Directed lifecycle tests

All checks below passed on frozen Core `955a50cbb5e8d928b6c7b0c78e1af062b835df44`.

| Check | Result | Evidence |
| --- | --- | --- |
| Release Core build | PASS | Release archive built cleanly (baseline warnings unchanged). |
| `run_payload_store.sh` | PASS | Static resident mapping, handle identity, generation invalidation, dormant bypass lifecycle. |
| `run_payload_banked.sh` | PASS | `payload_id % 4` bank identity and legacy arbitration contract. |
| `run_wad.sh` | PASS | Admission and rollback compatibility. |
| `run_epl2_schema.sh` | PASS | EP-L2 configuration schema. |
| `run_descriptor_mshr_integrated.sh` | PASS | Tag-sidecar consistency during and after drain. |
| C3 descriptor directed tests | PASS | Existing descriptor behavior remains compatible. |
| `run_m1_mode_switch.sh` | PASS | Enabled unsupported functional feature aborts fail-closed (expected abort verified by harness). |
| `git diff --check` | PASS | Core candidate and documentation closeout have no whitespace errors. |

The tests are lifecycle and default-off gates. They neither enable Unified/RO/
TVD/adaptive behavior nor constitute a mechanism performance experiment.
