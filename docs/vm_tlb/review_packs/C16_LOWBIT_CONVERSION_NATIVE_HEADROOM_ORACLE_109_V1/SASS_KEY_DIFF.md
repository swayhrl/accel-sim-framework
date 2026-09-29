# Baseline/oracle static SASS audit

The accepted grouped binary and the new baseline specialization have identical
key instruction counts and resource usage: 11 LDG, 10 LDS, 10 STS, 32 STG,
16 HMMA, 2 BAR.SYNC, and 80 registers with 9,984 bytes shared memory.

The oracle retains exactly the same 11 LDG, 10 LDS, 10 STS, 32 STG, 16 HMMA,
2 BAR.SYNC, and 9,984-byte shared-memory structure.  It uses 72 registers.
Conversion half operations change as intended:

- HADD2: 50 to 0
- HFMA2: 50 to 0
- LOP3: 50 to 86
- SHF: 31 to 22

Source dependencies combine every loaded qweight word with the loaded qzero and
all four loaded scale words before constructing the oracle MMA operand.  The
successful runtime canaries temporarily flipped the low bit of every element in
each compressed source and changed 6,291,456 qweight-dependent outputs,
6,291,456 qzero-dependent outputs, and all 12,582,912 scale-dependent outputs.

Therefore compressed loads, shared-memory staging, MMA work, barriers, and
output stores were not deleted.  The oracle is isolated enough for this local
diagnostic, but its new integer dependency chain is not claimed to be a free or
physically implementable operand source.
