# Directed lifecycle tests

All tests below passed against frozen Core candidate `955a50cbb5e8d928b6c7b0c78e1af062b835df44` after a release build.

| Test | Result | Contract exercised |
| --- | --- | --- |
| `tests/ep_l2/run_payload_store.sh` | PASS | Global IDs, static resident mapping, generation invalidation, bypass release. |
| `tests/ep_l2/run_payload_banked.sh` | PASS | Four-bank identity/arbitration contract. |
| `tests/ep_l2/run_wad.sh` | PASS | Admission/rollback compatibility. |
| `tests/ep_l2/run_epl2_schema.sh` | PASS | EP-L2 configuration schema. |
| `tests/ep_l2/run_descriptor_mshr_integrated.sh` | PASS | Sidecar consistency during and after drain. |
| C3 descriptor directed tests | PASS | Existing descriptor behavior remains compatible. |
| `tests/ep_l2/run_m1_mode_switch.sh` | PASS | Unsupported functional bit rejects fail-closed (expected abort verified by script). |

Release build: PASS. No mechanism experiment was run.
