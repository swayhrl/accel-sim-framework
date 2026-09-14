# Validation

- `python3 -m unittest discover -s tests/vm_tlb/c16/lane_h -p 'test_*.py' -v`: PASS, 11 tests.  This includes the added directed selected-PC/overlap test.
- `python3 -m py_compile util/vm_tlb/c16/lane_h/*.py tests/vm_tlb/c16/lane_h/test_*.py`: PASS.
- Selected prefill raw SHA256: PASS against its retained `SHA256SUMS` entry (`668f7f...5528b8`).
- Selected Decode1 raw SHA256: PASS against its retained `SHA256SUMS` entry (`dc8661...21bdc2`).
- Real parser canary: PASS.  Each raw stream parsed an explicit GLOBAL `LDG.E` record with mask `0xffffffff`, 32 reconstructed active lanes, width 4, and READ classification.  Selected `LDG.E.U16` PC analysis also completed.
- Exploratory analysis command: PASS; two captures, `SET_ONLY` model.

No check above is a C16 formal-admission pass.  In particular, the inputs lack
the committed `c16-trace-manifest-v1`, C16 receipt/terminal lineage, C16 S0
scenario identity, Decode2/3/4 windows, and a receipt-bound C16 runtime object
map.  Those gaps force the exploratory tier and `UNKNOWN_RUNTIME` attribution.
