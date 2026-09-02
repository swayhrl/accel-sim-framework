# Authorized minimal fixes

1. Framework `gpu-simulator` Makefiles now pass the Core, libcuda, and CUDA
   include roots to `makedepend`.  Generated trace-driven dependencies include
   `shader.h`, `gpu-sim.h`, `vm_translation.h`, and
   `abstract_hardware_model.h`; this prevents stale cross-repository ABI use.
2. Core `ldst_unit::memory_cycle` now supplies the ordinary global/local
   load/store access type before returning a translation `COAL_STALL`.  The
   stall was already modeled; this prevents an uninitialized statistics index
   from crashing the replay path.

Neither change alters page mapping, TLB/MSHR/PWQ/walker capacities, fixed walk
latency, request ordering, replay policy, or any frozen VM semantic.
