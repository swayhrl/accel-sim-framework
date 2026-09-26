# Engineering deviations and retained invalid results

No scientific target, parameter, or replacement domain was selected after
observing performance.

## Specialized/SFU unit source coupling

The preregistered T1 `TENSOR_2X` point changed specialized-unit count from 4
to 8 while keeping the frozen four-entry issue register. It terminated before
a performance result with:

`register_set::get_ready: Assertion 'reg_id < regs.size()' failed`

The constructor creates one issue-register id per unit, so unit count cannot be
scaled past the issue-register width as an isolated intervention. Increasing
both would change two resources. The result is retained as
`INVALID_SOURCE_COUPLING`, not a regression or speedup.

The same source relationship applies to `gpgpu_num_sfu_units` and the frozen
four-wide SFU issue register. T0 and L2 SFU points were therefore skipped before
execution and were not replaced with a third domain. Registry entries
`D1_SFU_UNITS` and `D1_TENSOR_SPECIALIZED_UNITS` are superseded from eligible
to `REJECTED_CONFOUNDED` for independent 2x scaling.

## Launcher receipt recovery

An efficiency correction stopped redundant per-arm grammar parsing after the
accepted trace qualifications and SHA gates had already been established. The
T1 L2-capacity simulator child had already started and was deliberately not
interrupted. Its launcher parent was gone when the child completed, so the
normal `rc.txt` write did not occur.

`recover_interrupted_run_receipt.py` accepts only this exact run and requires
the complete terminal, instruction/CTA, coverage, duplicate-application, and
quiescence signatures plus the exact L2-capacity override. It recovered rc=0
and wrote `RECEIPT_RECOVERY.json`; no scientific output was synthesized.

All accepted traces are still SHA-checked per arm. Re-parsing their full trace
grammar is no longer repeated for every resource setting.
