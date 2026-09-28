# C16 GPT-3 public-shape scale-transfer consumer scaffold

CPU-only Lane 6 preparation. Start with `AUTHORITY_AUDIT.json`, `OLD_QWEN_RECOMPUTE.tsv`, and `FORMULA_AND_SCHEMA_FREEZE.json`.

The producer gate is closed. No future result has been prefilled; new result tables contain headers only. The old Qwen values are independently recomputed from committed raw timing samples rather than copied from derived summaries.

Generator: `util/vm_tlb/c16/gpt3_shape_scale_transfer_consumer.py`.
