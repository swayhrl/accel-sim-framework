# FAST64.1 R2 closeout dependency freeze

Status: **FROZEN UNTIL `FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS`**

The full immutable R2 wave is live evidence. The following current closeout
dependencies are frozen in place; they must not be edited or restarted before
the existing closeout controller finishes strict 7/7 collection.

| path | SHA-256 |
| --- | --- |
| `util/dtc_l1/monitor_fast64_1_r2_closeout.sh` | `c0a7deab101dd3a95382ddad05bd3f3df537b1a4001a7737528e0029bed158be` |
| `util/dtc_l1/collect_fast64_1_r2_full_wave.sh` | `2125f6bd5abcf1f461c3dcc090bdf3b6e480077aaf96980099a2289f418fe4b7` |
| `util/dtc_l1/validate_fast64_trace_row.py` | `125c32256846949f2b93e7e71687017229ba3435c0d66206ab3d28af59f7af6c` |
| `util/dtc_l1/parse_dtc_l1_summary.py` | `7145b7f98d9138d1e49f662ea91e2a3e86644e7d6e853c80dffb053cc5253bc8` |
| `util/dtc_l1/compare_fast64_nonbinding_cap.py` | `13359ca46402ebcf5b5a0e30c091178a45068cbbf32267564c8f7f91343ccc5f` |
| `fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv` | `e9b9ccfcbb05f74016d5fcc2eedb63306e42b2a13b340b2dd36ce5ead5f63269` |
| `FAST64_BASE.config` | `1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde` |
| `FAST64_IO.config` | `d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621` |
| `FAST64_OO.config` | `546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa` |
| `FAST64_IO_CAP1048576.config` | `c0d169b83f4b30c2e19c77a83a67789e0733df20ea0da94525c37e194adc44ae` |
| `FAST64_OO_CAP1048576.config` | `b9c8716bffb4c35dad31f568fd9288e2bb6cbda995997a9912ff2b3ddab5b6d6` |
| `SM7_QV100/trace.config` | `19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e` |

This is execution/provenance protection, not a scientific acceptance gate.
Future FAST64.2/3 host-only preparation uses versioned, separate controllers
and may read these bytes but never changes them. The seven R2 rows and the
active `fast64-r2-closeout` controller are likewise not to be disturbed.
