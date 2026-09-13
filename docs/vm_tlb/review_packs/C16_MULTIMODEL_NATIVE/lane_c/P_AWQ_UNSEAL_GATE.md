# P AWQ cheap-catalog unseal gate

`Qwen7 AWQ` catalog payloads are not read during train/tune freeze.  Only `--apply-p-awq-holdout` after `P_TRAIN_SELECTOR_RULES_AND_12_24_48_PLANS_FROZEN_AWAITING_AWQ_CHEAP_CATALOG` may read the manifest-listed `PROSPECTIVE_QWEN7_AWQ` cheap catalog.  NCU/NVBit outcomes remain outside this gate.
