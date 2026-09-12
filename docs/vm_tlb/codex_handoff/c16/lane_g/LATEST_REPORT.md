# C16 Lane G handoff

Status: `C16_G_OFFLINE_GPU_PACKAGE_READY_WAITING_A_ASSETS`.

C16-0.3/0.4 offline infrastructure is ready: an actual CPython 3.10 Linux x86_64 wheelhouse with resolved transitive wheels, no-index resolver/install/import receipt, idempotent offline bootstrap, unified native runner, explicit Wave-1 adapters, nsys/NCU/NVBit wrappers, receipt schema, target second-pass identity guard, shared execution-budget ledger guard, and no-GPU dry-run validation. The receipt records `GPU_RUNTIME_VERIFY_REQUIRED`: it did not launch a CUDA kernel. All mock outputs are marked non-scientific and cannot enter a native catalog.

C16-0.9 is prepared but cannot close: A's fixed integration receipt hash-verifies model/input/scenario metadata, H's dedicated offline manifest is consumed as a non-dynamic protocol, and A's required GPU asset/input/scenario package remains unpublished. No AutoDL SSH/GPU was used, no models were downloaded, and no simulator run was started. Once A publishes a fixed hash-bound package and the user provides AutoDL SSH, proceed with C16-1 inline G0/G1/G2/G3 qualification; G0/G1 success immediately releases its corresponding work while G2/G3 remain nonblocking.

Execution safety closure: C16-1.1 must initialize the shared execution-budget ledger from an observed provider/AutoDL instance-start timestamp and its receipt path. Every real native runner, nsys, NCU, and NVBit command then requires that initialized ledger; it enforces the 24 GPU-instance-hour wall-clock envelope and separately records GPU-active operation time. NVBit additionally receives the remaining/per-window raw and time guard. Dry-runs need no ledger and remain non-scientific.
