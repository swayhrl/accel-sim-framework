# ULDC.64 checkpoint evidence

- First raw record: 0 0 5 3 0030 ffffffff 0 ULDC.64 0 0 0
- Corresponding postprocessed traceg record: 0030 ffffffff 0 ULDC.64 0 0 0
- Dynamic occurrence count: 7168.
- Dynamic PC: 0x0030; opcode: ULDC.64; active mask: 0xffffffff.
- NVBit MREF status: **0 MREF in the static instrumentation path**. The packet's is_mem=false/width 0 is source-backed: the host inserts a memory address only when an operand has type InstrType::OperandType::MREF; otherwise it passes is_mem=0. The device packet producer therefore leaves ma.is_mem=false; the shared formatter emits width 0 and immediate 0.
- Static SASS/instrumentation metadata available at checkpoint: opcode/PC above plus the source-backed MREF decision. A separate NVBit decoded-operand/SASS dump for this PC was not materialized before the review checkpoint; it is explicitly **NOT_CLAIMED**, rather than reconstructed from .64.
- Consumer failure: frozen consumer parser commit 25aa29862239a408099639ae9d5f1a0ea4fee1e1 returns TRACEG_GRAMMAR_REJECT: missing immediate. Its strict parser treats ULDC as a constant-memory access and consumes address fields after the zero-width field, making the final 0 appear to be an address mode and leaving no immediate field.
