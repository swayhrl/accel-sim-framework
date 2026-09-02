# G3-2A source-path proof

All source references below are to the diagnostic Core working tree anchored at
accepted commit `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`, with local,
uncommitted G3-2 diagnostic work.  The instrumentation records only existing
transactions at the VM hook; it does not alter an address, translation result,
queue, or resource decision.

## Trace global path

`gpu-simulator/trace-driven/trace_driven.cc:246-251` copies every trace lane
address directly into the warp instruction with `set_addr()`.  The opcode
decoder assigns `OP_STG` to `memory_store` and `global_space` at lines 284-292.
The first high address is the active-lane literal at BFS `kernel-7.traceg:1237`:
`STG.E.SYS`, PC `0x250`, active mask `00210180`, lane address
`0x00fffdc0000000cd`.

`src/abstract_hardware_model.cc:515-550` obtains an active lane's current
address and only forms an aligned segment/chunk transaction.  Thus the observed
`0xfffdc0000000c0` is the ordinary 32-byte coalesced form of the raw trace
address, not a new simulator address namespace.  The VM hook is
`src/gpgpu-sim/shader.cc:2408-2449`; it admits global/local/param-local
instructions and receives the already-coalesced `mem_access_t`.

## Local path is distinct and was not used by this offender

Trace execution invokes `translate_local_memaddr()` only for local memory at
`gpu-simulator/trace-driven/trace_driven.cc:628-641`.  Its shared-address-space
linearization implementation is
`src/gpgpu-sim/shader.cc:1872-1917`.  Coalescing separately recognizes
`local_space` / `param_space_local` in
`src/abstract_hardware_model.cc:526-543`.  The bounded LUD and BFS diagnostic
runs recorded no local or param-local transaction reaching the VM hook; this
is a bounded observation, not proof that such paths never exist.

## No recursive PTE classification

The offender is `GLOBAL_ACC_W` from a `global_space` `STG.E.SYS`, whereas a
PTE request is explicitly physical and translation-bypassing in
`src/gpgpu-sim/vm_translation.h:55-68`.  PTE responses are terminated before a
shader L1/LDST FIFO at `src/gpgpu-sim/shader.cc:4944-4951`.  Therefore the
captured offender is not a recursively translated `PTE_ACC_R` request.

The functional failure is the generic backend's range assertion at
`src/gpgpu-sim/vm_translation.cc:68-80`, specifically line 73, after the
normal VM hook has formed the VPN.
