# Source and path anchors

`mem_access_t` enters the VM hook after coalescing.  In functional mode,
`translation_controller::translate` holds data request issue until READY.
The path is:

`raw trace address -> coalesced SimVA -> L1 lookup launch/service -> shared L2
launch/service -> translation MSHR -> PWQ -> walker -> intermediate PWC ->
physical non-recursive PTE_ACC_R through L2/DRAM -> PTE response association ->
TLB fill/wakeup -> identity-like SimPA -> normal data-cache request`.

Relevant Core anchors at `5ba17a1b`:

- `src/gpgpu-sim/gpu-sim.cc`: parser defaults for 10/80 lookup service around
  lines 410–423 and controller construction around 1055.
- `src/gpgpu-sim/vm_translation.h`: state/counter contracts around 238–308 and
  lookup/waiter timestamp structures around 390–474.
- `src/gpgpu-sim/vm_translation.cc`: one-shot service state machine 467–539;
  MSHR registration/merge 541–581; monotonic requester accounting 589–635;
  pending bypass and READY return 637–704; wake/fill accounting 707–745.

PTE requests are physical and bypass translation; recursive translation is a
hard invariant.  PTE return identity checks request ID plus expected physical
address before advancing a walk.
