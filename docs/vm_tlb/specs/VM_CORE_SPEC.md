# VM core specification (M1)

Status: `MODELING_DECISION`, M1 closed.

The raw trace memory address is named `SimVA`. M1 preserves it on every
coalesced `mem_access_t`; translation records `SimPA`, and the downstream data
address is `SimPA`. M1's deterministic mapper uses 64KB pages and
`SimPPN = SimVPN`, so `SimPA == SimVA` while preserving both identities.

v0 scope is global, local, and local-parameter data transactions. Constant,
texture, instruction, PTE, page-fault, migration, UVM, MCM, segmentation, and
sub-entry behavior are outside M1. Translation state is intended to persist
across ordinary kernels in one context; M1 has no stateful TLB to flush.

Modes: `-gpgpu_vm_mode 0` is disabled; `1` is ideal identity with no latency or
queueing; `2` is reserved and explicitly aborts until M2 implements it.
