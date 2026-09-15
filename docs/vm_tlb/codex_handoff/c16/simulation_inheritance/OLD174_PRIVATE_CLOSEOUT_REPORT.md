# old174 private closeout report

Status: `OLD174_PRIVATE_CLOSEOUT_PASS_EXPORTED_PRIVATE_ASSETS`.

Using V1 authority `872423194e393fac9ca85171c77bafa87bde389e` and Round 2
coordination commit `4ca4ef4ab3f25319430b76f14ff69c1d69b158a4`, this pass
inspected old174 locally rather than self-SSH.  It closed every prior ODP
scope and exported five private-only scientific assets to
`/root/share/c12_c15_inheritance_exchange_v1/old174_private_export/`.

Exported tree SHA values are: C12 C5 raw
`087dd11bbd9b8f827652aca7ab54d5b971b6985b307f78d3282e443da95e511d`, C13
diagnostic raw `fc478aeed27032eab4d662e9dec57adabd84a4d4628559c9a0d584794f4b4ad7`,
C14 microdiagnostic raw `af59e57701fa2d55900527084fe63ce189dc46e72163f4b0b0a3acbf199f3681`,
C3 trace/control input `96dda0c033b0e9efc484d322c32e8fc81f3a305d91ad64a412ce7063c14e1472`,
and C12 pre-fix scan `85a37250305bea429123e96a1ee88dc558729fed2803400c234d6d01ced7d81f`.

C12's 22 raw-log SHA values and C13's ten repaired raw-log SHA values match
their Git provenance receipts.  C3 links depend on the old private stage, but
all 1,432 unique trace referents byte-match shared M4I counterparts, so stage
was not duplicated.  C13/C14 scientific boundaries and C12 candidate-arm
qualifications remain unchanged.  No simulation, GPU workload, deletion, or
ChatGPT handoff edit occurred.
