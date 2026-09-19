# LDC.U8 validator-only recovery

The old binary rejected real `LDC.U8` width=0. The isolated binary was rebuilt from the existing `implicit_constant_load_opcode` source rule, whose exact unit suite passed positive LDC and negative LDG/LDGSTS cases. The recovered P1 Step4 trace passed it with 504 LDC.U8 records. No producer raw data, address, width, consumer parser, or simulator semantics were weakened; the original failed formal attempt remains in its target directory.
