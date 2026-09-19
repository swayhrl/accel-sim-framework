# Hit-path timing semantic contract

Target override is activated by `GPGPUSIM_VM_TARGET_LOOKUP_KERNEL_UID` only when the active kernel UID equals Q05. Its L1/L2 values are passed to the existing `translation_controller` override map; no prefix kernel receives them. The override changes only effective lookup service latency. Capacities, associativity, ports, MSHR/PWQ/walkers/PWC/PTE and cache policy remain configured F0 values. The repaired downstream guard remains active and requires every access to have VM translation applied before admission.
