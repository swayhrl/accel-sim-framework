# Reproduce the independent CPU review

This packet runs on the preserved174-new environment with the fixed true164 packets, input bindings, closed native results and production source/binary paths recorded in the JSON reports. It does not capture new traces, run a simulator/GPU, register requests or alter V1. The old raw streams and CSV/resource files are read only after their accepted receipt/EXIT/hash gates.

The included `dtc_v2_d_*.py` scripts are the exact executed review sources. Every script refuses to overwrite its output report. To replay them, use a fresh private copy with only its D output-directory constant redirected to a new exclusive true164 directory. Keep all scientific source paths and SHA constants unchanged, run scripts in the order listed below, and preserve original frozen outputs. The source bridge reads the preceding fixed8 bound report. These scripts are separate review checks, not scientific experiments.

1. `dtc_v2_d_initial_audit.py`; `dtc_v2_d_cost_review.py`; `dtc_v2_d_root_math.py`.
2. `dtc_v2_d_b_closed_check.py`; `dtc_v2_d_b_csv_review.py`; `dtc_v2_d_v1_preservation.py`.
3. `dtc_v2_d_fixed8_bound.py`; `dtc_v2_d_parser_bridge.py`; `dtc_v2_d_b_source_root_contract.py`.
4. `dtc_v2_d_a_replay_review.py`; `dtc_v2_d_a1_matrix_review.py`; `dtc_v2_d_c_final_review.py`.

Use `python3 -B` for Python. The A/C independent replays themselves compile one fixture at a time with nice19 on CPU132,2GiB address-space,60s subprocess and zero-core-dump limits. Verify CPU132 is still legally free from protected jobs before any later replay; a different safeCPU only changes host execution placement, not scientific configuration. Initial legacy fixture compilation used nice15 with no concurrency and no model. CPU binaries stay private; their SHA and argv are recorded in reports.

Expected A outcomes are22 original and24 isolated-prototype cases, including intentional HOLD/assertion classes. Expected C outcomes are19 original-header cases plus2 deliberate SIGABRT cases. None establishes a universal liveness theorem or replaces future strict270-option/lifecycle/archive/native-restore acceptance. Present CPU-only authorization does not permit the16 planned simulations.
