# LDC.U8 semantic recovery boundary

The producer leaves constant operands without an NVBit MREF as width-zero,
addressless records.  The repaired validator accepts this only for exact base
opcode `LDC`.  It does not infer `.U8` as a dynamic one-byte access, nor create
an address.  The frozen simulator's existing `OP_LDC` path uses its own
implicit constant-load approximation (`data_size=4`), so this acceptance is
not a claim that the modeled operation is a true one-byte load.

All other address-bearing load/store records retain strict width/address
requirements; `ULDC` is not covered by this exception.
