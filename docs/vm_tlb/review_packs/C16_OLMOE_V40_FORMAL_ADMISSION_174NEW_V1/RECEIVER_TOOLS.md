# Independent receiver tools

## Selector canonicalizer

`util/vm_tlb/c16/olmoe_v40_receiver/selector_canonical_v1.py`

SHA256: `43d0e9acf29177aa09bf1c8e66d6849c4f44ccba90f938f1179d78a8e2445480`

The code independently implements `C16_SELECTOR_CANONICAL_V1`: strict UTF-8 TSV,
duplicate/malformed-field rejection, numeric static sorting, lexical column
sorting, exact string preservation, compact canonical JSON plus newline, and
SHA256. It does not import producer selector code.

Synthetic unit test:

`util/vm_tlb/c16/olmoe_v40_receiver/test_selector_canonical_v1.py`

SHA256: `d5ec53463bb857c114afeeef71907e07215bf0cce054ae910c69c76e93715a4a`

PASS: reordered rows preserve the hash; a field change changes it; duplicate
numeric static identity rejects; missing and extra TSV fields reject.

## Independent recompute

`util/vm_tlb/c16/olmoe_v40_receiver/recompute_243.py`

SHA256: `a66dfa368e5c45eab43133dba03db2454c17dca62fafe1fa7985bb2b6c9b9be5`

It reads only a destination selector and raw per-shard evidence: C16WARP1
trace/header/records, stdout terminal/accounting/occurrence evidence, supervisor
receipt, and ADDRESS_CONTEXT. It computes the executed/zero partition, separate
warp-record and active-lane counts, typed roles, and only
`SUM_OF_PER_SHARD_UNIQUES` locality values. It does not read producer 243 summary
or analysis files as input and contains no cross-shard VA/chronology/reuse/cache
analysis.

Bundle-dependent execution remains `NOT_RUN`.
