# Kernel-boundary source audit

`gpgpu_sim::m_vm_translation` is a simulator member (`gpu-sim.h:741`). `shader.cc:649` reinitializes shader/CTA state. `gpu-sim.cc:2363-2377` invalidates L1 when F0 flush_l1=1; L2 invalidation is separately config controlled. No reset/flush flag will be modified to manufacture warm state.
