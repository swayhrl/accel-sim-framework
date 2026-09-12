# C16 A local execution receipts

| Receipt | Command or method | Result | Cost/evidence boundary |
| --- | --- | --- | --- |
| C15 static selftest | `static_fingerprint.py --selftest` | T03/T04/T05/T06 PASS | CPU-only fixture/static validation |
| C15 static validate | `static_fingerprint.py --validate .../C15.../lane_a` | T01/T14/T20/T18/T22 PASS | CPU-only schema/provenance validation |
| C15 units | `python3 -m unittest tests/vm_tlb/c15/lane_a/test_static_fingerprint.py` | 11 PASS | CPU-only synthetic tests |
| C15 manifest closure | Git object reads plus SHA-256 recomputation | A 34, B 21, C 35 payloads match | read-only artifact commits only |
| C16 selftest | `c16_local_prep.py --selftest` | C16A_T01 PASS | CPU-only |
| C16 assets | `c16_local_prep.py --record-assets` | C16A_T02 PASS; 79 manifest rows | metadata/tokenizer downloads and remote LFS declarations only |
| C16 tokenization | `c16_local_prep.py --tokenize` | C16A_T03 PASS; 84 receipts | CPU-only `transformers==4.51.3`; no model load |
| C16 validate | `c16_local_prep.py --validate` | C16A_T04 PASS | local hashes and token derivations |
| C16 units | `python3 -m unittest tests/vm_tlb/c16/lane_a/test_c16_local_prep.py` | 4 PASS | CPU-only unit tests |

No GPU, CUDA/Torch model load, nsys, NCU, NVBit, Accel-Sim, SASS, or full-ROI
operation occurred in these receipts.
