# G2-1 — deterministic mapper and finite TLBs

Status: `PASS`  
Core: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`  
Framework: `8959f40ba88a28c6dffb7d5530064ea7c3710f2f`

`translation_key` is `(ASID, VPN, page_size)`. The deterministic resident
mapper uses `PPN = VPN`, preserving page offsets and preventing unintended
VPN aliases. A finite L1 TLB is created per SM and a single finite L2 TLB is
shared by the GPU. They are configurable set-associative structures with
deterministic LRU replacement and finite lookups-per-cycle ports. G2-1 uses
zero lookup latency; finite ports are the modeled resource constraint.

`ldst_unit::memory_cycle` requests translation before L1D/ICNT data-request
allocation. Only `READY` calls `mem_access_t::set_sim_pa`; a port stall returns
before data `mem_fetch` allocation. MSHR/PWQ/walker behavior is not claimed;
it is G2-2/G2-3 work.

## Directed evidence

`g++ -std=c++11 -Wall -Wextra -Isrc tests/vm_m2_g2_1_test.cc src/gpgpu-sim/vm_translation.cc -o /tmp/vm_m2_g2_1_test && /tmp/vm_m2_g2_1_test`

Result: `vm_m2_g2_1_test PASS`.

- one-page cold/hit: one mapper/L2 miss then one L1 hit;
- L1 capacity: deterministic two-eviction sequence and L2 hit;
- L2 capacity: deterministic two L2 evictions and three mapper resolutions;
- two SMs/same VPN: two private L1 misses, shared-L2 hit, one mapper lookup;
- page-size tag: same VPN 64KB/2MB tags do not falsely hit;
- finite lookup throughput: second same-cycle lookup is `L1_PORT_STALL`.

The standard Core+Framework build passed after this change; `git diff --check`
passed.

## Disabled-mode regression and runtime note

The disabled branch is unchanged and the controller is constructed only for
`-gpgpu_vm_mode 2`. The frozen M1 disabled/ideal transparency evidence remains
applicable to mode 0: `../M1_VM_CORE_FOUNDATION/VALIDATION_SUMMARY.md`.

Two bounded functional-mode LUD smoke attempts did not reach end statistics
inside their local 120/180-second budget and were terminated. No assertion,
deadlock, or request-loss report was emitted; they are explicitly not PASS
evidence. Raw logs: `/tmp/g2-1-qv-functional.log`,
`/tmp/g2-1-qv-functional-10k.log`, and
`/tmp/g2-1-qv-functional-100.log`.

## Source anchors

- `src/gpgpu-sim/vm_translation.{h,cc}`
- `src/gpgpu-sim/gpu-sim.{h,cc}`
- `src/gpgpu-sim/shader.cc`
- `tests/vm_m2_g2_1_test.cc`
