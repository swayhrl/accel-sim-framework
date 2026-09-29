# Stage A accepted-evidence decomposition

Stage A performs no simulator run. It consumes the hash-closed R101R2 B0/O2
raw data and the same six immutable zero-copy trace members.

## O2 queue depth

The accepted terminal O2 raw log reports:

- maximum scheduled depth: 1;
- maximum ready depth: 16.

These are observations of the unbounded pre-L1 O2 implementation, not proposed
queue sizes for S1 or H1.

## Exact accepted kernel boundaries

All requested kernel 4/5/6 boundaries are available from accepted raw.

| Arm | Kernel | End cycle | Kernel cycles | L1D access delta | L2 access delta | DRAM-read delta | DRAM-WB delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 | 4 XXT | 3,945,609 | 968,780 | 811,008 | 8,921,649 | 13,909 | 174,019 |
| B0 | 5 BA | 4,953,699 | 1,008,090 | 1,216,512 | 9,326,944 | 88 | 187,122 |
| B0 | 6 BMM-add | 5,962,148 | 1,008,449 | 1,441,792 | 11,715,443 | 731,172 | 721,804 |
| O2 | 4 XXT | 3,293,262 | 316,433 | 0 | 633 | 105 | 139 |
| O2 | 5 BA | 3,615,057 | 321,795 | 0 | 352 | 32 | 0 |
| O2 | 6 BMM-add | 4,107,499 | 492,442 | 0 | 25,488 | 3,072 | 892 |

The authoritative long-form cumulative fields remain in
`STAGE_A_EXISTING_EVIDENCE.tsv`.

## Coalesced region/opcode reconstruction

The offline decoder reproduces SM89's accepted arch-89, one-warp-part,
32-byte sector coalescing. It closes exactly against every O2 per-kernel
LDG/LDGSTS/WRITE count and request/active-byte counter:

- kernel 4: 8,110,008 X1 LDGSTS reads and 811,008 A2 writes;
- kernel 5: 405,504 A2 LDG reads, 8,110,008 A2 LDGSTS reads,
  72 same-kernel B2 LDGSTS reads and 811,008 B2 writes;
- kernel 6: 3,424,232 B2 LDGSTS reads, 720,896 X1 LDG reads,
  6,823,936 X1 LDGSTS reads and 720,896 X0-generation2 writes.

Measured totals are exactly 29,937,568 transactions and 958,002,176 request
and active bytes.

The detailed composition is in `REGION_OPCODE_COMPOSITION.tsv`.

## Producer/consumer availability

The line/sector ledger uses 128-byte lines, four 32-byte sectors and an exact
32-bit byte mask per sector. Only a producer in an earlier completed kernel is
upgraded to legally available data. Same-kernel serialization in trace files is
reported separately and is not claimed to be simulator runtime chronology.

The main cross-kernel chains are:

- context kernel 3 produces X1 generation1, consumed by measured kernels 4 and
  6;
- measured kernel 4 produces A generation2, consumed by kernel 5;
- measured kernel 5 produces B generation2, consumed by kernel 6.

Of 27,594,656 measured read transactions, 27,594,584 have byte-complete data
from an earlier real producer store. The remaining 72 B2 reads occur in the
same kernel that produces B2 and are not upgraded by the offline ledger.

Initial X0 generation1 has no producer inside the six-member CONTEXT2 view.
The ledger therefore does not treat it as preloadable. Kernel 6's X0
generation2 writes have no later consumer inside this view.

The compact aggregate is `PRODUCER_CONSUMER_AVAILABILITY.tsv`. The
8,740,881-row per-line/sector ledger is hash-closed on node164 and is explicitly
a data-availability ledger, not cache residency or an MRC.
