# Static and dry-run validation

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

The following checks passed in B9 without simulator/worker/miner execution:

| Check | Result | Scope |
|---|---|---|
| `python3 -m py_compile` for selector, manifest validator, and resource validator | PASS | Syntax only |
| `bash -n util/vm_tlb/run_b9_e01_e10_after_a_terminal.sh` | PASS | Syntax only |
| `validate_b9_execution_pack.py` | PASS: 16 arms, 24 whitelist rows, 32 selector rows | Text config stack and file/hash validation only |
| `select_b9_matched_kernels.py --dry-run` | PASS: 16 prefill + 16 decode1 | Kernel-list text plus file metadata only; no trace content opened |
| `validate_b9_resource_gate.py` | PASS: 7 synthetic normal/calibrated/pressure cases | Synthetic values only |
| future helper default `--dry-run` | PASS: command manifest rendered; effective concurrency declared 1 | No A attestation, resource gate, output directory, simulator, or miner invoked |

The manifest validator verified expected effective VM settings for every target
arm: finite PWC 32/512, ideal PWC, 2 MiB page diagnostic, disabled VM, and
ideal identity. It also verifies the frozen 24-row delta whitelist and 16+16
selector cardinality. A later run must revalidate current hashes immediately
before launch; a mismatch is `INVALID_CONFIG`, not an implementation patch.
