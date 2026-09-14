# C16 Analysis Prep 174-new V1

Decision: `ANALYSIS_PREP_PASS` for the CPU-only foundation.  This pack binds
analysis consumption to pipeline implementation `3c4847d2da818013dca6422194af36966136ab31`,
the canonical root `/root/share/mnt164/huangrulin/c16_ai_workload`, and
`FORMAL_ADMISSION_CONCURRENCY=1`.

The RTX3090 Q2 corpus is a read-only parser/fingerprint regression fixture.
The newly reconciled RTX4080 R5 objects are an artifact/provenance closure, not
a cross-model result.  N1 and R5 NCU sources remain separately classified.

All large parser outputs and receipts are under the canonical root's
`derived/`; this Git pack contains only compact review evidence.  The entrypoint
is `util/vm_tlb/c16/analysis/c16_analysis.py analyze-run`: it verifies a
cataloged run manifest before parsing, writes hash-closed derived products, and
deterministically rebuilds both indexes.  It invokes neither GPU software nor a
tokenizer.
