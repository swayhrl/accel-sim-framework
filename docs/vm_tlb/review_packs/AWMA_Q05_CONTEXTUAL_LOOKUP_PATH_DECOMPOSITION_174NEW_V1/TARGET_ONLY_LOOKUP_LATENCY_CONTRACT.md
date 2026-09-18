# Target-only lookup latency contract

`GPGPUSIM_VM_TARGET_LOOKUP_KERNEL_UID`, `..._L1_LATENCY`, and `..._L2_LATENCY` are disabled by default. On the first exact target Q05 translation request, shader code verifies target uid and asks the persistent controller to install an idempotent override only after its predecessor translation state is quiescent. The override lives in an ABI-neutral controller-pointer registry.

It changes only target L1/L2 lookup service/ready latency. TLB contents, capacity, associativity, replacement, port arbitration, MSHR/PWQ/walker/PWC/PTE paths, mapping, caches, and predecessor execution remain natural. Zero latency uses the pre-existing same-cycle service path.
