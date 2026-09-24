# AWMA RTX4080/V1 ideal-translation control V2 — A1 semantic stop

Status: `A1_SEMANTIC_GATE_FAILED_STOP`.

V2 preserves the frozen V1 `pipelined_launch` resident accessq prelaunch branch,
scan direction, READY ownership, `consume_ready` argument, and downstream
admission policy. Ideal translation resolves the same current functional
page-table mapping at that existing V1 observation point and removes all modeled
translation service state.

## A1 directed T2 evidence

| mode | cycles | instructions | eligible UID count | eligible UID FNV64 |
| --- | ---: | ---: | ---: | ---: |
| OFF | 93079 | 43357696 | 411008 | 39910020883933566435 |
| ideal | 83713 | 43357696 | 411008 | 130352204422296124267 |

OFF reproduced the accepted V1 10/80 cycle count. Both modes had zero
untranslated/unobserved accesses and duplicate attempts. Ideal had zero modeled
translation lookup/MSHR/PWQ/walker/PTW/PWC/PTE state.

However, the exact eligible UID sets differ despite equal cardinality. Earlier
ideal head application changes whether later prelaunch scans see an entry as
already applied. Therefore V2 still fails the required equality of V1 prelaunch
eligibility semantics. No new T0/T1/T2 ideal matrix runs were started. The V1
full-kernel results remain `INVALID_DIAGNOSTIC`.
