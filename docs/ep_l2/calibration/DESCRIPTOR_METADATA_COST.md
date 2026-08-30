# EP-L2 descriptor 256 -> 512 metadata cost

Status: **D512_COST_READY**. This is a raw metadata-capacity estimate, not a
technology-area or performance estimate.

## Verified model facts

The C7e model holds a shared per-slice `m_descriptor_pool`; its capacity is
configured by `-gpgpu_ep_l2_descriptor_pool_size`, and the formal baseline is
256 with a per-line cap of 32. The model's `ep_l2_descriptor` contains a
`mem_fetch *`, a four-sector mask, and a response-queued bit. It is allocated
when a request is appended and returned only after response injection. See
`src/gpgpu-sim/gpu-cache.h` (`ep_l2_descriptor`, around lines 1198-1206) and
`src/gpgpu-sim/gpu-cache.cc` (allocation around lines 698-708; reclaim around
865-880) at Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`.

The C++ pointer, vector/list nodes, allocator overhead, debug statistics, and
the complete host `mem_fetch` object are deliberately **not** counted as
hardware state.

## Hardware mapping assumptions

A physical descriptor must retain the response identity/routing information
that the model reaches through `m_mf`, the requested sector mask, response
state, and an association to the line transaction. Exact routing and
transaction-tag widths are not fixed by this model, so the table is a range.

| Field group | Minimal packed estimate | Conservative packed estimate | Basis |
| --- | ---: | ---: | --- |
| valid/free + response/state | 2 b | 4 b | model has `m_response_queued`; physical allocator needs liveness |
| sector/request mask | 4 b | 4 b | four 32-B sectors per 128-B line |
| response routing/request endpoint | 12 b | 24 b | architecture-dependent requester/return path |
| transaction/request identity | 16 b | 32 b | implementation choice; not a host pointer |
| line-MSHR association | 7 b | 7 b | 128 Line-MSHRs |
| pool/list linkage or descriptor index | 9 b | 9 b | accommodate a 512-entry pool |
| access/order/type bookkeeping | 4 b | 16 b | model-dependent persistent request semantics |
| **raw subtotal** | **54 b** | **96 b** | |
| **implemented SRAM word assumption** | **64 b** | **128 b** | byte-aligned/word-rounded range |

The 64-bit lower point assumes the descriptor refers to existing transaction
state and carries only a compact return token. The 128-bit upper point assumes
an explicit request tag and more complete routing/access state. A 96-bit
midpoint is shown for planning only. This is intentionally a storage estimate,
not an SRAM-area claim; compiler/layout, ECC, banking, and process node would
all change area.

## Capacity cost

The only requested expansion is 256 additional descriptors per L2 slice. The
frozen machine has 64 slices and a 144 KiB/slice unified payload budget (9 MiB
chip total).

| Assumed descriptor word | 256 entries/slice | 512 entries/slice | Increment/slice | Increment/chip (64 slices) | Increment / 144 KiB slice payload | Increment / 9 MiB chip payload |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64 b (8 B) | 2 KiB | 4 KiB | 2 KiB | 128 KiB | 1.39% | 1.39% |
| 96 b (12 B) | 3 KiB | 6 KiB | 3 KiB | 192 KiB | 2.08% | 2.08% |
| 128 b (16 B) | 4 KiB | 8 KiB | 4 KiB | 256 KiB | 2.78% | 2.78% |

The incremental storage is therefore 128--256 KiB chip-wide before any ECC,
parity, allocator/free-list metadata, or physical banking overhead. If those
are included later, they must be stated separately rather than folded into the
descriptor word silently.

## Comparison boundary

No defensible tag/MSHR/WAD bit comparison is emitted yet: their physical
field layouts are not fixed by the C++ containers. The applicable comparison
for this calibration decision is the frozen payload budget above. D512 is
plausible enough to test, but this estimate does not promote it as a baseline
or claim a performance benefit.
