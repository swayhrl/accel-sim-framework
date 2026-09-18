# Q05 contiguous prefix capture V1 — formal review stop

Status: `STOP_FOR_SCIENTIFIC_REVIEW`

R1 single-target regression passed. R2 launches 33--34 same-context canary
passed: both raw members terminally closed, passed frozen grammar validation,
and the frozen workload continued naturally.

P34 formal capture produced all 35 same-context raw members in the required
order, but member 2 is rejected by the frozen grammar:

```
TRACEG_GRAMMAR_REJECT: memory opcode has zero/missing width: LDC.U8
```

Member 2 is an interior predecessor and cannot be omitted. The raw data is
diagnostic-only and is not admitted or published. No width/address is inferred
or fabricated, no grammar rule is relaxed, and no node164 context bundle ACK
is requested.
