# Cost boundary

The prototype adds one versioned stable-hash evaluation and one integer
threshold comparison for target admission. The hash datapath contains a
64-bit key/seed XOR, one add, two 64-bit multiply-mix stages, shifts/XORs, and
a 64-bit comparison. Class identity and region-relative line index come from
the existing oracle interval lookup. Stable eligibility can be recomputed, so
the prototype does not require a per-line selector bit; existing protected and
class metadata are unchanged.

Hardware latency, throughput impact, power, and area have not been evaluated.
The software prototype is not evidence of zero hardware cost.
