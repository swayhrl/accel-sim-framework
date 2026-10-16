# Incremental storage/port ledger, no RTL estimate

| Item | Bound to implementation | Parameterized accounting / unknown |
|---|---|---|
| Data array | same sole R0 allocator, 1168 x128B per slice for WBUF16; no new production data array | R0 WBUF8 total1160 remains contract, not newly qualified here |
| Copy latch | existing common 128B/slice pipeline latch on both R0 B/U sides | unchanged; not counted as a lendable payload slot |
| Role | RESIDENT/BYPASS/WB/TVD | four roles fit 2 bits, same encoded width as R0's three roles |
| Payload state | ten enum states including TVD_VALID/TVD_INFLIGHT vs R0 eight | ceil(log2(10))=4 vs3 bits if dense encoding; simulator C++ enum size is not physical area |
| Combined address directory | reuses 128 WAD address identities, not WAD128+TVD128 | existing line address/mandatory identity plus payload ID11, payload generation Gp, entry generation Gd, state3, valid4, dirty4, readers R, age A; exact overlap/delta depends on chosen R0 RTL packing |
| Frontend lease | one head request, lookup-cycle identity, handle/ticket/mask and pin | existing D512 not enlarged; cycle stamps/counter widths are instrumentation rather than automatic silicon charges |
| Arbiter | existing four banks, single op per bank/cycle; TVD_READ shares it | TVD read and WB lower-read requests can deny one another; no extra payload port |
| Tag and metadata | same-bank eligible-way promotion and serialized +1cycle directory lookup | added compare/select/mux/control/generation cost; RTL timing, CAM implementation and technology-specific area/power unknown |

The C++ directory has born/lower_accept/age/revision timestamps, 64-bit generations and statistics; these establish model ordering and evidence. Do not multiply sizeof(entry) as a hardware area claim. Keep protocol metadata widths parameterized, identify overlap with R0 WAD and state constraints, and carry physical implementation unknowns. Packet version backing and the test map are functional simulator/reference data, not a second production payload RAM. No extra physical data capacity or new free hardware bank bandwidth is claimed.
