# M4I-4 address and metadata admission

Status: `PASS` for the authorized 49-bit paper-facing contract.

The immutable full-ROI coverage outputs were rehashed in place:

| ROI | final coverage SHA256 | width | addresses >= 2^49 / >= 2^56 | max SimVA |
| --- | --- | ---: | --- | --- |
| prefill | `6fd209619fae6e348afd109933fe90cf9828d2e65d461b5dc50ccc90d6f4ab5a` | 47 | 0 / 0 | `0x7fddf3808007` |
| decode1 | `dc56d89e0e3e6c1f1483fa560fdecf8d4183ac56c15b679911da094a2096c828` | 47 | 0 / 0 | `0x7f81ecb88007` |

The integrated decoder's fresh one-trace resumable smoke passed for each ROI
with zero decoder failures and zero >=49-bit or >=56-bit references.  No
address masking, truncation, canonicalization, or relocation occurred.

Each immutable ROI sidecar contains one contiguous `WEIGHT` allocation of
1,012,011,008 bytes: prefill starts at `0x7fd99e000000`, decode1 at
`0x7f7ec6000000`.  Each has 128 observed KV events.  RF0 proves no ambiguous
Weight/KV overlap, validates the ROI-temporal KV selection, and binds the
range map plus sidecar identity before later classification/registration.
Thus the frozen Weight descriptor candidate and the existing 49-bit config are
admitted; no synthetic KV is present.
