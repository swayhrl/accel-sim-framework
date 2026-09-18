# Target-only I0 semantic contract

The diagnostic is disabled unless `GPGPUSIM_VM_TARGET_I0_KERNEL_UID` is a positive decimal uid. For that exact currently-running kernel only, `ldst_unit::memory_cycle()` uses the accepted mode-1 identity SimVA→SimPA operation and does not call L1/L2 TLB, MSHR, PTW, PWC or PTE paths. All other kernels—including every predecessor—remain F0 `gpgpu_vm_mode=2` natural translation.

Source gate: the accepted page backend resolves `ppn = key.vpn`; natural Q05 deltas show `vm_identity_equal == vm_ideal_translations`. Thus target I0 produces the same downstream SimPA for this admitted input. The formal row lists bind the target to trace member 34 and launch uid 3/9/35 (P2/P8/P34); no cache flush, reset, preload, trace mutation or formal-bundle mutation is performed.
