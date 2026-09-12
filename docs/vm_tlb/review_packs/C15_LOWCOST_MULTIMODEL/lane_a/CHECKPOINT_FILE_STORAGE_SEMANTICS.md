# Checkpoint-file storage semantics

All static byte and alias facts in this publication concern Safetensors
checkpoint-file data offsets. They do not describe GPU physical addresses,
virtual addresses, runtime allocations, residency, cache/TLB state, or execution
time.

- `WEIGHT_STORAGE_BREAKDOWN.tsv.checkpoint_file_storage_bytes` is the union of
  exact data-offset ranges per shard and storage dtype. Its former
  `physical_bytes` label has been retired because it could be misread as GPU PA.
- `STATIC_FOOTPRINT.tsv.allocated_payload_bytes` is a legacy quantity name
  required by the static-footprint schema. Here it means only the same
  checkpoint-file offset union; its assumptions explicitly reject VA/PA and
  runtime allocation interpretation.
- `TENSOR_ALIAS_AUDIT.tsv.exact_file_range_alias_observed` reports equality of
  two named ranges in the same checkpoint-file shard. It is independent from
  `config_tie_declaration` / `semantic_tying_status` and never establishes GPU
  physical sharing.
