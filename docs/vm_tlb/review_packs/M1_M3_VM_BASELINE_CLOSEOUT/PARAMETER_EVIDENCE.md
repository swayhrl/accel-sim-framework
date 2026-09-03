# Parameter evidence boundary

`PAPER_SPEC`: 64KB baseline, 32-entry fully-associative L1, 768-entry/16-way
L2 and 16 walkers.  `MODELING_DECISION` / `REFERENCE_OTHER_PAPER`: generic
56-bit backend width, balanced radix prefixes, intermediate-only PWC,
PWC-128, MSHR/PWQ sizing, and 10/80 lookup service timing.  The latter are not
claimed as Segmentation-paper or commercial-GPU exact parameters.

The 2MB run is generic foundation coverage, not a page-promotion policy.  The
49-bit configuration remains a directed compatibility proof; the generic M3
result configuration is 56-bit.  Fixed PTW and zero lookup service are tagged
diagnostic, never formal timing results.
