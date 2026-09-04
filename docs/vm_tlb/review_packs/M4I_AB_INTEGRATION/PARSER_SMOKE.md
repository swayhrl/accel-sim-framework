# M4I-5 final-Core parser smoke

Status: `PASS`.

Fresh one-entry, symlink-only fixtures were made from the immutable staged
`.traceg.xz` files and run with the final Core/Framework SM86 configuration.
Each run reached `bind to kernel 1` without an unsupported-format/opcode,
`ERROR`, or assertion.  A bounded timeout (`124`) after bind is an intentional
smoke result, not a failed parser run.

| ROI/sample | semantic class | result |
| --- | --- | --- |
| prefill early / middle / late | COMPUTE | bind PASS |
| prefill NCCL | NCCL_COLLECTIVE | bind PASS |
| decode1 early / middle / late | COMPUTE | bind PASS |
| decode1 NCCL | NCCL_COLLECTIVE | bind PASS |

The prefill early compute sample also bound in all three VM entries:
`CONTROL_VM_DISABLED`, ideal-identity, and functional VM.  This confirms that
the final VM hook did not corrupt parser/startup state.  No trace was rewritten
to obtain these results.
