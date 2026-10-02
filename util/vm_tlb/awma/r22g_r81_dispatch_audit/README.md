# R22G R81 dispatch audit

`audit_rule_u01.py` is a standard-library-only CPU script. It verifies selected
node109 R81 raw files against the accepted parent `RAW_DATA_INDEX.tsv`, joins A0
and A3 only at matched `(cohort, repetition, step)` keys, applies the frozen
RULE_U01 threshold, and emits the retrospective and nondeployable-oracle tables.

It does not import Torch, access CUDA, regenerate model outputs, or modify the
parent authority.
