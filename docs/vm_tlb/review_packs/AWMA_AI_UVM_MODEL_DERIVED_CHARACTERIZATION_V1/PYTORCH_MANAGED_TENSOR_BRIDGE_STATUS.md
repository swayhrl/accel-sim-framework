# PyTorch managed-tensor bridge status

Status: `NOT_READY`. Exactly one bounded attempt was made for a 4096x4096 BF16 managed weight followed by `torch.mv`. Compilation stopped before GPU execution because `cuda_runtime_api.h` was absent from the extension compiler include path. The attempt was not retried, and no allocator/framework modification was made.

Attempt source SHA256: `f05214c1ac8b900e3b32c7343defca9ebe05d72e911edf4e5fdfa4f3773cf107`.
