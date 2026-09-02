# Allocation and tensor sidecar schema

Schema: `m4a-allocation-sidecar-v1`.  The sidecar is separate from NVBit SASS
trace files and uses the simulator-input address label `SimVA`; it makes no
claim about the exact NVIDIA internal address stage.

```json
{
  "schema_version": "m4a-allocation-sidecar-v1",
  "run": {"run_id": "string", "model_id": "string", "model_revision": "string", "classification": "PAPER_COMPATIBLE_SELF_CAPTURE"},
  "allocations": [{
    "allocation_id": "string", "simva_start": "0x...", "size_bytes": 4096,
    "object_kind": "WEIGHT", "tensor_name": "optional", "layer": "optional",
    "lifetime": {"start_phase": "MODEL_LOAD", "end_phase": "DECODE"},
    "classification_provenance": "runtime hook / allocator observation"
  }],
  "phases": [{"name": "MODEL_LOAD|PREFILL|DECODE", "kernel_selector": "optional"}]
}
```

`object_kind` is exactly one of `WEIGHT`, `KV_CACHE`, `ACTIVATION`,
`WORKSPACE`, or `UNKNOWN`.  `SYNTHETIC_KV` is prohibited in this stage.
Active ranges must not overlap unless an explicit future schema extension
explains aliasing. Unknown allocations remain `UNKNOWN`.

The Route-E wrapper also writes `weight_layout`: one `WEIGHT` allocation ID,
256-byte alignment, and deterministic per-parameter name/offset/size rows.
Its runtime binder checks parameters remain views into one buffer after
prefill/decode and fails on a detected post-load storage replacement. This is
a GPU-virtual-buffer check only; physical contiguity remains an M4A-C check.

`util/llm_trace_capture/validate_metadata.py` validates syntax, non-overlap,
positive sizes, phase names, and optional trace-address coverage.  GPU VA
stability and trace coverage are M4A-C checks, not asserted by M4A-P.
