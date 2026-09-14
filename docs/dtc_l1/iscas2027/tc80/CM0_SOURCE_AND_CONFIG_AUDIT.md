# CM0 — TC80 source and configuration feasibility audit

Status: **PASS — exact 80 KiB is representable config-only**

This is a source/configuration audit only.  It launched no simulator and did
not alter FAST64, Lane E, traces, the Core, or any frozen scientific evidence.

## Audited identities

| item | identity |
| --- | --- |
| TC80 framework start | `f16e75960f9e97a4ea51c9b997a24d52bb96c7bb` |
| frozen B16 config | `configs/dtc_l1/fast64/FAST64_BASE.config` (`1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde`) |
| frozen formal Core source | `hrl/decoupled-l1-m5-v0@95ccdb7a056f2d53f740d90869785cac6d4ee0f5` |
| frozen formal runtime | `/tmp/dtc-fast64-zero-access-formal-95ccdb7a/accel-sim.out` (`462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`) |

The source-object IDs inspected at Core `95ccdb7a` are `gpu-cache.h`
`f270808bb0d2cf6e0c6a77fa2f8c7185073b812c`, `gpu-cache.cc`
`351b4d89f587897b4113730db7f534189b652687`, `gpu-sim.cc`
`fca511ee16016ad230b37a021c1ca084d3d19e28`, `shader.cc`
`efed7d77d340e14b5c57c1ff0788c8304e043bb6`, and `gpu-misc.cc`
`020443a04e36cb825c9121faa29bf82f2c623593`.  The post-FAST64 observer
descendant changes only `gpu-sim.cc`/`shader.cc`; it was not selected as a
runtime or scientific input for TC80.

## B16 is the conventional cache path retained by TC80

The frozen B16 config resolves `-gpgpu_cache:dl1` to
`S:32:128:4,L:T:m:L:L,A:512:8,16:0,32`, `-gpgpu_dtc_l1_mode 1`,
`-gpgpu_dtc_l1_pib_entries 8`, `-gpgpu_dtc_l1_mshr_entries 32`, four L1
banks, and `-gpgpu_l1_latency 20`.  Its terminal startup log echoes all of
these values; see the immutable B16 raw log
`/workspace/fast64-repaired-ramp3/fast64_atax_base_core95ccdb7a_a1_r1/simulator.stdout`
lines 51–59 and 92.

`cache_config::init` parses the set count, line size, associativity,
replacement/write/allocation/index function, MSHR fields, queues and port
width from `-gpgpu_cache:dl1` (Core `src/gpgpu-sim/gpu-cache.h:576–776`).
The actual searchable conventional line count is `m_nset * m_assoc`
(`gpu-cache.h:787–790`), and its emitted geometry is
`m_line_sz * m_nset * m_assoc` (`gpu-cache.h:799–802`).  Therefore B16 is
`32 × 4 × 128 = 16,384 B`; TC80 can be exactly
`32 × 20 × 128 = 81,920 B = 80 KiB = 640 lines`.

`baseline_cache` constructs the ordinary `tag_array` and conventional MSHR
table from that config (`gpu-cache.cc:2235–2247`).  `tag_array` allocates
ordinary line/sector blocks (`gpu-cache.cc:189–204`), probes each conventional
way at `set_index * m_assoc + way` (`gpu-cache.cc:252–263`), and selects an
invalid or LRU/FIFO victim over the same unconstrained way loop
(`gpu-cache.cc:287–333`).  There is no associativity power-of-two test or
maximum in this path: 20-way is source legal.  Reserved lines are excluded
from replacement and return `RESERVATION_FAIL` only if all ways are reserved
(`gpu-cache.cc:287–323`).  Conventional MSHR merge/allocation is owned by
`baseline_cache::send_read_request` (`gpu-cache.cc:1406–1456`); Core
`shader.h:2393–2396` overrides the parsed `A:512` field to the frozen
PAPER_BASE traditional-MSHR value 32.  Thus TC80 keeps the B16 effective
MSHR=32 rather than changing it with cache capacity.

## Indexing, banks, latency, and exact geometry

The selected B16 function is linear `L`.  It indexes with
`(addr >> m_line_sz_log2) & (m_nset - 1)` (`gpu-cache.cc:138–140`), after
`m_nset_log2 = LOGB2(m_nset)` (`gpu-cache.h:688–689`).  Consequently a
source-correct linear configuration requires a power-of-two set count.
All power-of-two factors of 640 are enumerated in
[`CM0_GEOMETRY_CANDIDATES.tsv`](CM0_GEOMETRY_CANDIDATES.tsv).  The chosen
`32 sets × 20 ways` is exactly representable and retains B16's 32-set mapping;
it was selected before any performance result exists.  Candidate set counts
that are not powers of two are deliberately excluded because the bit-mask
indexing would not cover them correctly.  The Fermi hash is irrelevant here
and separately limits itself to 32 or 64 sets (`gpu-cache.cc:97–117`).

The four-bank mapping is independent of cache geometry: `l1d_cache_config`
hashes only with `l1_banks` and its byte-interleaving fields
(`gpu-cache.cc:68–75`).  The TC80 overlay therefore retains four banks,
32-B data-port width, all queue fields and all policies.  L1 latency is the
independent `-gpgpu_l1_latency` option (`gpu-sim.cc:399–400`) and the latency
queue is sized from that option (`shader.cc:4245–4249`); the overlay retains
20 cycles.

There is one required capacity-geometry companion field.  `l1d_cache_config`
uses `-gpgpu_unified_l1d_size` to compute an allocation multiplier and asserts
that it divides the configured L1 size (`gpu-cache.h:935–945`).  The frozen
128-KiB value does not divide 80 KiB.  TC80 must therefore set it to 80 KiB,
which yields multiplier one and allocates the exact 640 conventional entries.
This is not a memory-system change: it is mechanically required by the
selected L1 capacity representation and is classified as
`DERIVED_FROM_REQUIRED_GEOMETRY` in CM1.  No source change is needed.

The runtime configuration echo is the final authority for the selected
`-gpgpu_cache:dl1` tuple and the 80-KiB unified value; the CM2/CM3 validators
will parse that echo, require `sets=32`, `ways=20`, `line_bytes=128`,
`lines=640`, and `bytes=81,920`, and reject an otherwise successful run if
any field differs.

## Mode separation and inactive state

The frozen B16 comparator deliberately retains `PAPER_BASE`, rather than
switching to `LEGACY`: `shader.h:2393–2396` preserves its B16 MSHR override
and `shader.cc:3554–3579` uses its fixed 8-entry admission/Tag-service gate
before conventional `m_L1D->access`.  This is the accepted B16 conventional
Tag/Data path; it has ordinary `tag_array` allocation, conventional MSHR
merging and no tag-to-physical-line rename.

In `PAPER_BASE`, the Core constructs only `paper_frontend`; IO and OO front
ends are instantiated only for modes 2 and 3 (`shader.cc:4261–4298`).  TC80
will keep mode 1 and hence keeps all IO/OO physical-pool, duplicate,
in-flight/response, FIFO/OO retirement and reference-count state inactive.
It also leaves the DTC physical-line parameters present in the inherited
config but unreachable; the validator will require no `PAPER_IO`/`PAPER_OO`
mode echo and no IO/OO counter family in a TC80 output.  This preserves the
frozen B16 admission and traditional-MSHR behavior without importing DTC
IO/OO lifetime semantics.

## CM0 conclusion

`TC80_S32_W20` is an exact, source-legal, config-only 80-KiB conventional
geometry.  It preserves B16's 128-B line, set mapping, bank/request geometry,
latency, policies, effective PIB=8 and effective MSHR=32.  CM1 may create one
canonical overlay only; no alternative is authorized as a second primary
geometry.
