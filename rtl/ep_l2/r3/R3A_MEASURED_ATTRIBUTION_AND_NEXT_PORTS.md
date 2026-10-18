# R3A measured attribution — corrected final view

Sourceac607 independently complete required finite qualification. Old first
checkpoint/grouping tables remain immutable. The earlier grouping helper missed
single-parameter Yosys module names, merging realTag-map/GEN engines into top.
Corrected source-controlled actual_cost_r1/MODULE_ATTRIBUTION.csv recognizes both
name forms; all wholecut area/FF/WNS totals were unchanged by that correction.

A areas B16/S64/U1437416.652/1478834.714/1847603.016; FF88685/90833/121550;
WNS−1.370226/−1.393728/−1.447954ns and2ns also negative. U/B1.2853636.
U Tag-map remains1024words,84439.040 area/11264FF; two sharedGEN engines
313.880 area/0FF. Metadata totals503616.736/515810.176/692212.864. Exact
seq/comb/top decomposition and WNS/TNS in correctedCSV plus actual rawreports.

Five functionalGENreads remain; source19→17 mux instances does NOT mean two
physicalports saved because lower GENread becomes real. All32-bitGEN FF retained.
Both A and finalB actually tested same-bank different-row simultaneous FE+lower
GEN updates under P1 data service, including same16slot metadata group; no
one-writer-per-bank or1RW SRAM assumption. Highest1167/bank3/drain passedA in
3379cycles, same as frozenR2. All14actualA binaries decoded/source/fixture checked.

Remaining bank-local GEN/read routing could reduce global paths, but must keep
two independent metadata writers per bank where FE/lower coincide. A possible
up-to8bank-local engines or a changed pipeline is UNIMPLEMENTED/UNMEASURED;
no saving or fixed GPU extra cycle inferred. Tag-index pins/sector needs paid
inverse resolution and true field ports. SRAM/nativeTag/MSHR/NoC remainUNKNOWN;
no wholeL2/net benefit/lower-bound claim. FinalB is selected for qualified owner
state removal and lower area; it is not bestWNS in every static mode.
