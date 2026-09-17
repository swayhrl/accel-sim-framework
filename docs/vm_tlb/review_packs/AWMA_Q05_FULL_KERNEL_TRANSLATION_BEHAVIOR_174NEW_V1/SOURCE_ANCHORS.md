# Source anchors

- `vm_translation.cc:132-201`: empty object-map path disables attribution and returns `OBJECT_UNKNOWN`.
- `shader.cc:2444-2480`: VM mode 1 applies identity translation and asserts equal SimVA/SimPA; mode 2 invokes functional translation.
- `vm_translation.cc`: object attribution is guarded and records observability counters; this stage does not alter mapping/timing.
- `memory_telemetry.cc` and `export_m4c_telemetry.py`: aggregate telemetry source/exporter used for existing bounded receipts.