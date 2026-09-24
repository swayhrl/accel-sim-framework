# AWMA RTX4080/V1 ideal-translation control V3

Status: `COMPLETE_CURRENT_BASELINE_IDEAL_CONTROL`.

V3 parent: `ba9fb5173fe3fa974734c20403f990b9f6349910`.

## Semantic contract

V3 preserves V1's resident accessq visibility, candidate predicate, reverse
scan order, head observation point, READY ownership, `consume_ready` policy and
downstream admission/arbitration. The ideal path exists only within that same
controller `translate` call and resolves the current functional page-table
mapping without modeled lookup, queue, TLB, MSHR, PTW, PWC or PTE state.

V3 does not require equality of the realized prelaunch eligible set: earlier
legal translation completion may make an entry applied before a later scan.
The frozen control law, not treatment-dependent schedule state, is invariant.

## A1 mapping audit

The directed T2 OFF/ideal pair had the same functional mapping digest:

`unique=134 fnv64=2001588591594167847`.

OFF reproduced accepted T2 V1 10/80 cycle count `93079`. Ideal had zero modeled
translation-service state. The realized eligible sets differ and are retained as
observational evidence only.

## Final matrix

| target | C_10_80 | C_0_80 | C_ideal | S_L1 | S_ALL |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | 527896 | 496170 | 446880 | 0.060098959 | 0.153469623 |
| T1 | 665802 | 664805 | 715636 | 0.001497442 | -0.074848078 |
| T2 | 93079 | 83439 | 83713 | 0.103567937 | 0.100624201 |

`S_L1=(C_10_80-C_0_80)/C_10_80` and
`S_ALL=(C_10_80-C_ideal)/C_10_80`.

`S_ALL` is the causal response to this ideal-translation intervention. It is
not an address-translation runtime fraction, and `S_ALL-S_L1` is not a PTW time
fraction.

## Final gates

For T0/T1/T2: expected instruction counts and unique UID coverage match;
untranslated=0; unobserved=0; duplicate attempts=0; quiescent invariants hold;
and modeled lookup/MSHR/PWQ/walker activity is zero. Mapping digests are:

| target | unique keys | FNV64 |
| --- | ---: | ---: |
| T0 | 256 | 4551608701457240867 |
| T1 | 493 | 12947203714122211934 |
| T2 | 134 | 2001588591594167847 |
