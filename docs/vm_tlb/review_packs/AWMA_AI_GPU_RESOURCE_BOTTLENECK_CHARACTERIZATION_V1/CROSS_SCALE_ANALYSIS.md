# Cross-scale analysis

## L1/M1 exact-function pair

The Native authority establishes identical function SHA, 67,464 simulated
instructions/CTA, 514 dynamic memory instructions/CTA, 16,388 active-lane
references/CTA, and 770 logical requests/CTA. L1 has 2,048 CTAs and M1 has 256,
an exact 8x aggregate scale relationship.

| metric | L1 scale-8 | M1 scale-1 |
|---|---:|---:|
| baseline cycles/CTA | 156.645 | 223.074 |
| baseline L1 reservation failures/CTA | 10,457.550 | 7,409.930 |
| L1-MSHR 2x failures/CTA | 7,159.894 | 3,229.781 |
| L1-MSHR 2x cycle response | +7.415% | +2.171% |
| DRAM 2x cycle response | +7.634% | +1.905% |

The same local architectural work therefore does not imply the same aggregate
resource response. L1 sustains more concurrent CTAs and greater reservation /
queue pressure, while M1 has poorer cycles/CTA because its smaller grid exposes
less whole-device parallelism. The result is evidence of execution-scale
sensitivity, not evidence that one model family is intrinsically different.

## Historical Qwen GEMV context

Accepted T2/A1/A2 evidence already showed that translation-path response varies
with context. This stage does not rerun or fold those results into a resource
average. T2's new resource response is reported only for its exact trace:
L1-MSHR +2.842% and DRAM +1.295%. Historical context sensitivity supports
keeping context as a variable; it does not establish a common scaling law.
