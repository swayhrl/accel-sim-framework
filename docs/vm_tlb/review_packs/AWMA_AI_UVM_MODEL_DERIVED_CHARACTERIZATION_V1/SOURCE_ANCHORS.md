# Source anchors and change scope

- Accepted pilot: `hrl/awma-ai-uvm-oversubscription-feasibility-pilot-v1@368b7043c70c1274f29153b5d5a665d1742aeacb`.
- Accepted continuation handoff: `hrl/awma-post-novelty-reset-handoff-v1@9e230e5bf8a5ad7b425d1d90c852f6771e200521`.
- Execution branch: `hrl/awma-ai-uvm-model-derived-characterization-v1`, branched from the accepted pilot.
- Local model revisions, config hashes, safetensors file hashes, and per-tensor identities are in `MODEL_ASSET_METADATA.tsv` and `MODEL_ASSET_SUMMARY.tsv`.
- Frozen route authority is hash-bound in `PREREG_FREEZE_RECEIPT.json`.

Changed code is confined to `util/vm_tlb/awma/uvm_pilot/`: local metadata extraction, one read-only route capture, preregistration freeze, a model-derived managed-memory replay harness, sequential locked runner, telemetry analysis, one bounded bridge attempt, and finalization. No accepted baseline, simulator, model, or UVM mechanism semantics were modified.
