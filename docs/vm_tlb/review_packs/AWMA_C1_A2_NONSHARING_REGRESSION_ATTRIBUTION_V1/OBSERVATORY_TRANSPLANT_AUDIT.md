# Observatory transplant audit

Status: `PASS`

## Authorities

- frozen mechanism: `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
- accepted observatory: `b85d388abe98e5da70b749b52075c33fad7cede4`
- Pair-A evidence: `9e7e6e3bbe3f3867dbf089ec3b97d5d51507776f`
- accepted observatory patch SHA-256:
  `ff53a7863fcc914714c6ab9a6aa970c38a71285ec7c4dda87e787ccc73cec976`
- diagnostic binary SHA-256:
  `85be8041f590340cf58a9239d941f722d32f25cd7cc633aec855fbd4c33d4d0c`

## Frozen mechanism delta

The frozen mechanism delta remains entirely authoritative.  In particular,
`vm_translation.cc` and `vm_translation.h` are byte-identical to the accepted
candidate hashes.  Candidate selection, proactive owner path, fallback,
READY-share delivery, translation frontend, and owner/readmission accounting are
unchanged.

## Observer-only delta

The exact accepted Observatory patch adds only:

- `bottleneck_observatory.h/.cc`;
- read-only scheduler/progress/translation/admission/cache/queue hooks in
  `shader.cc`, `gpu-sim.cc`, `l2cache.cc`, and `dram.cc`.

It does not mutate arbitration, queue contents, issue, READY ownership,
translation lookup, owner/fallback policy, cache replacement, request address,
or memory scheduling.

The patch applied cleanly to the frozen candidate with source offsets.  A copy of
the resulting diagnostic source was reverse-patched; all four touched frozen
files then compared byte-for-byte equal to their pre-transplant copies.  The two
mechanism files were never touched.  `CANDIDATE_SOURCE_FREEZE.tsv` records the
hashes.

## Semantic gate

With Observatory Level 0, the same diagnostic binary exactly reproduced:

| target | OFF | frozen candidate |
|---|---:|---:|
| A1 | 114123 | 112023 |
| A2 | 117698 | 125427 |

All four runs also preserve `34883072` instructions, `224` CTAs, `409024`
unique UIDs, accepted coverage-admission counts, `untranslated=0`,
`unobserved=0`, duplicate application `=0`, and terminal quiescence.  Level 0
emits no Observatory records.

Platform config SHA-256:
`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`.
Trace config SHA-256:
`a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`.
