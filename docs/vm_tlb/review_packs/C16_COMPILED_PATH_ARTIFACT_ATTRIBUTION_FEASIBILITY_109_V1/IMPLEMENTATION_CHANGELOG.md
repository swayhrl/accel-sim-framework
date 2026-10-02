# Implementation and provenance

The branch `hrl/c16-compiled-path-artifact-attribution-feasibility-109-v1` starts at the accepted Observer V2 failure commit `c48331a9ea5a3f381741aad4bae91dfb0eefc2c2`. Its earlier Mode B correctness authority is `9122fac5c50dbf19706636fc03978a356ffd800f`; the installed vLLM source matches `ced6857afa0ea7b2e3f0846a62e1394e90f15607` for the Qwen2 model file.

New stdlib-only analysis code under `util/vm_tlb/c16/compiled_path_artifact_attribution/` reads the pinned raw runtime JSON, cache file bytes and existing kernel-name inventory. `survey.py` verifies original and current cache identities; `pickle_scan.py` and `nested_scan.py` inspect pickle opcodes without deserializing; `provenance_map.py` joins FX/module paths, generated output-code comments and runtime names; `inventory.py` records explicit artifact presence; `validate.py` independently checks hashes, joins and decision gates; `closeout.py` emits this review pack. No runtime, model, cache or simulator source file was modified.

Review evidence begins at `README.md`; `ARTIFACT_FILE_INDEX.tsv` is the raw cache index by path/size/SHA. No large cache blob is committed. Git commit history for the branch remains the authoritative change log.
