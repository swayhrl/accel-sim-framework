# Runtime wrapper preparation

`fixed_window_replay.py` first runs formal admission with the compiled real
traceg parser, verifies `SIM_BASELINE_ID`, qualified binary SHA256, and an
accepted base-config SHA256, then builds an effective config from a restricted
input-specific overlay.

The overlay permits exactly one of each:

```text
-gpgpu_vm_object_map <hash-preserved compatibility view>
-gpgpu_vm_weight_segment_map <hash-preserved compatibility view>
-gpgpu_max_cycle 10000
```

The wrapper hashes the overlay and both referenced assets, preserves the raw
log and effective config, requires the established telemetry exporter, and
records command/environment receipts. Exporter failure or empty output makes
the CLI fail closed even when the simulator itself reached its expected
boundary. The future command shape is:

```text
python3 util/vm_tlb/awma/simulation/fixed_window_replay.py run \
  --manifest <producer-bundle>/SIM_INPUT_MANIFEST.json \
  --parser build/awma/traceg_grammar_smoke \
  --baseline-identity docs/vm_tlb/review_packs/AWMA_SIM_CONSUMER_PREP_174NEW_V1/BASELINE_IDENTITY.json \
  --binary <qualified-34deedd9-binary> \
  --base-config configs/vm_tlb/c5_configs/C11_C5_PREFILL_F0.config \
  --overlay <derived-hash-bound>/current-model-10k.overlay \
  --output-dir <new-immutable-run-directory> \
  --telemetry-exporter util/vm_tlb/export_m4c_telemetry.py
```

Execution status is one of `EXPECTED_FIXED_WINDOW_BOUNDARY`,
`NORMAL_COMPLETION`, `PARSER_ABORT`, `SIMULATOR_ASSERT_OR_FATAL`, or
`EXTERNAL_RUNTIME_FAILURE`. Only a zero exit with the boundary marker and
`gpu_sim_cycle = 10000` is the expected bounded stop. It is never full ROI.
