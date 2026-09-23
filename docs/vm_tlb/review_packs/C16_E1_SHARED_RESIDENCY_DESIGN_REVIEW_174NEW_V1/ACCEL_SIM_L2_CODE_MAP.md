# Accel-Sim / GPGPU-Sim L2 Code Map

## Scope and source identity

Evidence label: `VERIFIED_CODE`.

This map is a read-only inspection of the accepted Core authority
`swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`.  The coordinating
Accel-Sim Framework checkout does not embed a Core source tree; the inspected
local snapshot is:

`/root/workspace/awma_runtime_preserved_before_ldgdepbar_hotfix_174new_v1/src/gpgpu-sim-57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

The snapshot files below were byte-compared with a fresh detached checkout of
the exact accepted commit.  All comparisons passed.

| File | Git blob at `57bb71e` | SHA-256 of inspected file |
|---|---|---|
| `src/abstract_hardware_model.h` | `3f976d9f04998a347cb5ff1ccba33aac3a868585` | `d673124f94576446b84011220e6fa57cb62c9d320c6bf7c8f9a048d6b5343a36` |
| `src/gpgpu-sim/gpu-cache.h` | `01654a50b92dcfcc75ee9d8d030db7d7d38393f6` | `5ef6f6d26ffa4b162a41b6f6d55d5a4506075875fde31597710055f66a0a5bcf` |
| `src/gpgpu-sim/gpu-cache.cc` | `f7d276d6a09875359ef4ec61d7a1553a56e23745` | `8b8fcc3f9356da6005d0898c50298553270484ba58bcab1765ef5615e75d7cbb` |
| `src/gpgpu-sim/l2cache.h` | `65c9c38b358281200fd74f9a5aed02e372cd0ba0` | `80d1c2e23e0cacdbc84067cdc21a4992bfb0f2ad38cdef0309539c043f340fc8` |
| `src/gpgpu-sim/l2cache.cc` | `9d74a991beafa204bfa4cfe5b7e742588e4d6376` | `881d5708a0a0f0b021d528cd64600e42c4de28aa89daed1f2f3542a3ba9d9073` |
| `src/gpgpu-sim/mem_fetch.h` | `33ee855d42ffe52de0730a8249ccec76b7420895` | `5699cff6ef9a6a38b75c36b0dbd53ddd43bdaffb4faee6c4e04b7dc4b0a81922` |
| `src/gpgpu-sim/mem_fetch.cc` | `fd5cca99d115c3b8d5ad391915c3556324b20085` | `0a2b0820b9b01539f6187408efec09ff71fb1f197213afde344df0708d64e0cd` |
| `src/gpgpu-sim/shader.h` | `0df8e2cd1d8fa4d2fbbafc4d13c262c54c97db14` | `79515d24e1a662d9d3b75265f247a4e5fefc06907fdb23593a60ad07e2b8b307` |
| `src/gpgpu-sim/shader.cc` | `1e0e111ecc9f3d0795712e8fabfa0f5981290dda` | `74b358a1a001411e6eafd8f64436377bef51661f3ac645895b4312387725f6f3` |

Line numbers in this document refer to those exact blobs.

## Object ownership and request path

There is one `memory_sub_partition` per configured memory subpartition.  It
owns `class l2_cache *m_L2cache`, its lower-memory interface and four internal
queues (`m_icnt_L2_queue`, `m_L2_dram_queue`, `m_dram_L2_queue`, and
`m_L2_icnt_queue`): `src/gpgpu-sim/l2cache.h:162-241`, especially
`memory_sub_partition::m_L2cache` at lines 210-217 and the queues at 226-232.

`memory_sub_partition::memory_sub_partition` constructs the object as
`new l2_cache("L2_bank_%03d", m_config->m_L2_config, ..., L2_GPU_CACHE)`:
`src/gpgpu-sim/l2cache.cc:425-456`.  Therefore the modeled L2 is banked by
memory subpartition, rather than being one monolithic `l2_cache` C++ object.
The configuration object is `memory_config::m_L2_config`; command-line option
`-gpgpu_cache:dl2` supplies its string (`src/gpgpu-sim/gpu-sim.cc:253-257`),
and initialization calls `m_L2_config.init(&m_address_mapping)`
(`src/gpgpu-sim/gpu-sim.h:303-310`).

The inheritance/ownership chain is:

`memory_sub_partition -> l2_cache -> data_cache -> baseline_cache -> tag_array -> cache_block_t[]`

- `l2_cache` is the L2-specific subclass and currently delegates its access to
  `data_cache::access`: `src/gpgpu-sim/gpu-cache.h:1744-1760` and
  `src/gpgpu-sim/gpu-cache.cc:2032-2039`.
- `baseline_cache` constructs and owns the `tag_array`, MSHR table, miss queue,
  port model, and L2-level statistics identity:
  `src/gpgpu-sim/gpu-cache.h:1295-1321,1397-1498`.
- `tag_array` allocates either `line_cache_block` or `sector_cache_block` for
  every configured line: `src/gpgpu-sim/gpu-cache.cc:188-203`.
- L2 set indexing removes memory-partition-select bits before applying the
  configured cache set hash: `l2_cache_config::set_index`,
  `src/gpgpu-sim/gpu-cache.cc:156-169`.  Generic linear/XOR/IPOLY/Fermi hash
  selection is in `cache_config::hash_function`, lines 76-153.

During `memory_sub_partition::cache_cycle`, an admitted request at the head of
`m_icnt_L2_queue` is passed unchanged as a pointer to
`m_L2cache->access(mf->get_addr(), mf, ...)`; hits reply toward interconnect,
accepted misses leave via the L2 miss queue, and reservation failures retry in
place: `src/gpgpu-sim/l2cache.cc:469-607`, with the actual L2 call at 523-538
and outcome handling at 550-597.  Returning memory responses invoke
`m_L2cache->fill(...)` at lines 500-510.  `baseline_cache::cycle` drains one
miss-queue request to the lower-memory port (`src/gpgpu-sim/gpu-cache.cc:1225-1238`).

## Cache-block metadata

The common `cache_block_t` contains exactly:

- `m_tag` and `m_block_addr`;
- an observation-only `m_telemetry_class` deliberately separated from tag and
  replacement state;
- virtual state/time/mask operations implemented by the concrete line or
  sector block.

See `src/gpgpu-sim/gpu-cache.h:132-188`.

For a normal line, `line_cache_block` stores allocation, last-access and fill
timestamps; one `INVALID/RESERVED/VALID/MODIFIED` state; fill-control/readable
flags; and a dirty-byte mask: `src/gpgpu-sim/gpu-cache.h:190-301`.  Allocation
sets `m_alloc_time` and `m_last_access_time` to the allocation time and sets
the state to `RESERVED` (201-213); fill changes it to `VALID` or `MODIFIED` and
records `m_fill_time` (214-225).

For a sector cache, `sector_cache_block` holds per-sector allocation,
last-access and fill times, per-sector states and flags, plus line-level
allocation/last-access/fill times and one dirty-byte mask:
`src/gpgpu-sim/gpu-cache.h:303-530`.  Replacement uses the line-level time,
not an independent per-sector victim (`get_last_access_time` at 450-460 and
`get_alloc_time` at 462).

There is no protected/persisting bit, priority class, owner PC, region ID,
kernel UID, warp ID, CTA ID, or protected-occupancy counter in either concrete
cache-block representation at this commit.  The existing
`m_telemetry_class` is explicitly observation-only and must not be silently
repurposed as functional replacement metadata.

## Replacement policy and victim selection

The only configured replacement-policy enum values are `LRU` and `FIFO`
(`src/gpgpu-sim/gpu-cache.h:532`).  The cache-string parser maps `L` to LRU and
`F` to FIFO (`cache_config::init`, `src/gpgpu-sim/gpu-cache.h:587-625`); the
selected value is `cache_config::m_replacement_policy` at lines 875-913.

`tag_array::probe` is the victim selector:
`src/gpgpu-sim/gpu-cache.cc:239-332`.

1. It computes the set and full block-address tag (251-252), then scans every
   way in that set (260-317).
2. Matching `RESERVED`, `VALID`, or readable `MODIFIED` sectors return
   `HIT_RESERVED` or `HIT` immediately (263-281).
3. Reserved lines are ineligible.  An unreserved invalid line is remembered.
   For valid lines, the scan also enforces the dirty-line policy: clean lines
   are eligible, while dirty lines become eligible only when the global dirty
   percentage has reached `m_wr_percent` (286-315).
4. LRU chooses the eligible line with the smallest `get_last_access_time`;
   FIFO chooses the smallest `get_alloc_time` (302-313).
5. An invalid line is preferred over the selected valid victim (324-328).
   If every line is reserved, the probe returns `RESERVATION_FAIL` (318-321).

This is a timestamp-based policy, not an explicit ordered LRU stack.  There is
no target-aware victim filter or target/non-target preference in the accepted
implementation.

`data_cache::access` first probes, then dispatches the result to the configured
read/write hit/miss handler (`src/gpgpu-sim/gpu-cache.cc:1954-2020`).  Read hits
and write-back/write-through hits call `tag_array::access` to update state
(`rd_hit_base`, lines 1842-1861; `wr_hit_wb`, 1447-1464; `wr_hit_wt`,
1466-1492).  Inside `tag_array::access`, both `HIT` and `HIT_RESERVED` update
last-access time (`src/gpgpu-sim/gpu-cache.cc:344-357`).  A miss under
allocate-on-miss records any valid/dirty victim, allocates the selected block,
and copies only the request telemetry class into the block (358-378).

## Allocation, insertion, and fill

There is no separate insertion-priority abstraction.  The effective insertion
state is created by the concrete block's `allocate` method:

- normal-line allocation sets allocation time = last-access time = current
  time and state = `RESERVED`: `src/gpgpu-sim/gpu-cache.h:201-213`;
- sector line/sector allocation sets corresponding sector time and the
  line-level last-access time: `src/gpgpu-sim/gpu-cache.h:323-379`.

For allocate-on-miss, allocation happens in `tag_array::access` before the
lower-memory request is queued (`src/gpgpu-sim/gpu-cache.cc:358-378`), and
`baseline_cache::send_read_request` remembers the selected cache index in
`m_extra_mf_fields` while changing the outgoing request to the MSHR atom
address/size (`src/gpgpu-sim/gpu-cache.cc:1364-1405`).

On response, `baseline_cache::fill` restores the request address/size and:

- fills the previously reserved index for `ON_MISS`; or
- invokes address-based `tag_array::fill` for `ON_FILL`.

It then marks the MSHR ready and accounts for the fill port:
`src/gpgpu-sim/gpu-cache.cc:1240-1287`.  Index-based fill changes the concrete
block to valid/modified and copies the request telemetry class
(`tag_array::fill(unsigned,...)`, lines 449-457).  Address-based fill performs
victim probe/allocation at fill time and then fills the line/sector
(`tag_array::fill(addr,...)`, lines 407-447).  Fill records fill time but does
not independently promote LRU recency beyond the allocation/last-access state
already established.

Dirty victim information is carried in `evicted_block_info` (block address,
modified size, telemetry class, byte mask and sector mask),
`src/gpgpu-sim/gpu-cache.h:85-112`.  `rd_miss_base` and write-allocate paths
construct an L2 writeback `mem_fetch` when necessary; for the ordinary read
miss path see `src/gpgpu-sim/gpu-cache.cc:1866-1903`.

## Metadata present on a request reaching L2

The central carrier is `mem_fetch`, whose source-information members are
`m_request_uid`, `m_sid`, `m_tpc`, and `m_wid`; it also owns a `mem_access_t`, a
copy of `warp_inst_t`, stream ID, request/reply type, size, address-decoder
fields, timestamps, and optional original-request pointers:
`src/gpgpu-sim/mem_fetch.h:54-202`.  Its constructor copies the instruction
only when a non-null instruction is supplied and asserts that its warp ID
matches: `src/gpgpu-sim/mem_fetch.cc:37-85`.

The originating shader allocator passes the issued `warp_inst_t` into
`mem_fetch`, preserving its instruction PC and warp ID for ordinary shader
requests: `shader_core_mem_fetch_allocator::alloc`,
`src/gpgpu-sim/shader.h:2077-2109`.  However, sector-cache admission may split
a wider request before L2.  `memory_sub_partition::breakdown_request_to_sector_requests`
creates each child with the original pointer and copies access masks/type,
wid/sid/tpc/stream, but `partition_mf_allocator::alloc` constructs the child
with a null instruction: `src/gpgpu-sim/l2cache.cc:64-75,738-805`.  Thus a
split child's own `get_pc()` returns `-1`; the original request pointer remains
available, but current L2 access/replacement code does not dereference it to
recover PC.  Internal writeback/write-allocate requests can likewise have no
instruction and use sentinel source IDs.

| Requested identity | Directly present/reliable at the L2 access call? | Exact code evidence and boundary |
|---|---|---|
| Current address | **Yes.** | `mem_fetch::get_addr()` exposes `m_access.get_addr()` (`mem_fetch.h:88-91`), and `cache_cycle` passes it to `l2_cache::access` (`l2cache.cc:523-538`). `mem_access_t` holds current address plus SimVA/SimPA (`abstract_hardware_model.h:842-881,952-970`), but `mem_fetch` exposes only the current address, not SimVA/SimPA getters. |
| PC | **Conditional, not reliable for every L2 request.** | `mem_fetch::get_pc()` reads copied `m_inst.pc`, or returns `-1` if the instruction is empty (`mem_fetch.h:142-143`). Ordinary shader requests copy the instruction (`shader.h:2095-2102`); L2 sector-split children are constructed with null instruction (`l2cache.cc:64-75,738-805`). An `original_mf` pointer exists (`mem_fetch.h:150-151,196-201`) but is not used by current L2 lookup/replacement. |
| Access type / read-write | **Yes.** | `mem_access_t::m_type` and `m_write` are exposed through `mem_fetch::get_access_type()` / `get_is_write()` (`abstract_hardware_model.h:845-869,883-888,952-969`; `mem_fetch.h:88-116`). The enum distinguishes global/local/constant/texture, reads/writes, writebacks, write-allocates, instruction and PTE reads (`abstract_hardware_model.h:772-790`). Split children explicitly copy the type (`l2cache.cc:752-797`). |
| Instruction memory-space object | **Conditional, not a standalone request field.** | `warp_inst_t` inherits `inst_t::space` (`abstract_hardware_model.h:1014-1127`) and can be reached through `get_inst()` only when an instruction was copied (`mem_fetch.h:142-143`). It is absent from split/internal children. The robust field at L2 is the `mem_access_type` above. |
| Kernel UID | **No.** | Neither `mem_access_t` (`abstract_hardware_model.h:842-970`) nor `mem_fetch` (`mem_fetch.h:54-202`) contains a kernel UID or kernel pointer. `mem_access_t::get_uid()` is a memory-access UID (875), `warp_inst_t::get_uid()` is an instruction UID (`abstract_hardware_model.h:1321-1324`), and `mem_fetch::get_request_uid()` is a request UID (`mem_fetch.h:95`); none is a kernel launch UID. |
| Warp ID | **Yes for originating application requests; sentinel possible for internally generated requests.** | Explicit `m_wid` and `get_wid()` are at `mem_fetch.h:96-98,153-159`; shader allocation supplies `inst.warp_id()` (`shader.h:2095-2102`), and sector splitting copies it (`l2cache.cc:752-797`). Some allocator calls intentionally pass `-1`, e.g. writebacks in `gpu-cache.cc:1889-1899`. |
| CTA ID | **No.** | No CTA field/getter exists in `mem_access_t`, `warp_inst_t`, or `mem_fetch` at the cited class definitions. The shader owns CTA-to-warp state elsewhere, but it is not copied into the request reaching L2. |
| Shader/core and cluster IDs | **Yes, subject to internal-request sentinels.** | `m_sid` / `m_tpc` and getters are explicit (`mem_fetch.h:96-98,153-159`); shader allocation supplies core/cluster IDs (`shader.h:2077-2108`), and splitting copies them (`l2cache.cc:752-797`). |
| Stream ID | **Yes.** | Stored as `m_streamID`, getter at `mem_fetch.h:114,188`; copied by both shader allocation and sector splitting. |
| Active-lane, byte, and sector masks | **Yes.** | Stored by `mem_access_t` and exposed by `mem_fetch` at `mem_fetch.h:132-140`; split children preserve/refine them in `l2cache.cc:738-805`. |
| Exact qweight/region identity | **No dedicated field.** | Only address and the observation-only coarse telemetry class are present. There is no region-base/region-size ID or persisting-policy identity in `mem_fetch` or `cache_block_t`. |

## Consequences for the shared-residency design review

1. **Oracle/software-region tagging is implementable from address, but is not
   already represented.**  A future opt-in mechanism can compare the current
   L2 request address against an explicitly configured exact interval, then
   carry a dedicated functional target tag.  The specification must state
   whether matching uses current SimPA or preserved SimVA; the existing
   `mem_fetch` L2 interface exposes only `get_addr()`.
2. **Static-PC detection is not plug-in ready.**  Although many unsplit shader
   requests retain PC, sector-split and internally generated L2 requests do
   not have a valid PC in their own `mem_fetch`.  A PC classifier would require
   explicit, tested PC propagation/normalization across these paths; it must
   not treat `get_pc() == -1` as a real signature or confuse access/instruction/
   request UIDs with kernel UID.
3. **Kernel- or CTA-scoped detection has no direct request field.**  Adding it
   would be new metadata plumbing, not merely a victim-policy edit.  Warp ID is
   available for ordinary requests but is not universal for synthetic/internal
   traffic.
4. **The clean replacement-policy seam is localized.**  Target-aware victim
   preference belongs around `tag_array::probe`; insertion and hit/lifetime
   updates belong in `tag_array::access`, concrete block allocation/fill, and
   the fill path.  A functional protected tag must be a new field separate
   from the existing observation-only telemetry class.
5. **Baseline compatibility is structurally testable.**  With any future
   feature disabled, the existing LRU/FIFO candidate eligibility, dirty-line
   rule, allocation/fill timestamps, MSHR behavior, queueing, and writeback
   creation must remain byte-for-byte/decision-for-decision equivalent.  This
   document maps seams only; it does not authorize or implement a mechanism.

## Audit boundary

No GPU, NVBit, trace capture, simulator source mutation, build, or mechanism
simulation was performed.  This is a static code map of the accepted Core
commit only; it makes no claim about undocumented NVIDIA hardware behavior.
