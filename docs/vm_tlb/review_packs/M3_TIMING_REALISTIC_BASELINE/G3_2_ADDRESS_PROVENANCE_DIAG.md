# G3-2A — address provenance diagnostic

Status: `PASS — CASE A; STOP FOR CHATGPT ARCHITECTURE REVIEW`

This is a diagnostic acceptance only.  It does **not** resume G3-2 or
authorize G3-3/PWC.

| Item | Value |
| --- | --- |
| Accepted Core anchor | `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` |
| Core diagnostic source state | local, uncommitted G3-2 WIP plus isolated VM-hook recorder; not accepted or pushed |
| Framework handoff read | `971b1f46b74ed5eaaf4447d416a47f0e3e22d733` |
| BFS trace | `/tmp/s1-b0-smoke/rodinia_2.0-ft/9.1/bfs-rodinia-2.0-ft/__data_graph4096_txt___data_graph4096_result_txt/traces/kernelslist.g` |
| RTX3070 configuration | `configs/tested-cfgs/SM86_RTX3070/{gpgpusim.config,trace.config}` |
| Functional reproduction config | `/tmp/g3-2-vm-real-small-tlb.config` |
| Page size / ASID | unchanged: 64KB / ASID 0 |

## D0 — exact first offender

The first functional-mode request that reaches the existing 49-bit backend
assertion is a real BFS kernel-7 global store:

| Field | Value |
| --- | --- |
| Kernel UID / name | `7` / `_Z6KernelP4NodePiPbS2_S2_S1_i` |
| PC / operation / access type | `0x250` / store / `GLOBAL_ACC_W` |
| SimVA | `0xfffdc0000000c0` / `72055120136765632` |
| VPN (64KB) | `0xfffdc00000` / `1099473879040` |
| Required address width | 56 bits |
| Request UID / SID / TPC / WID | `114757` / `2` / `2` / `6` |
| Transaction size / page crossing | 32B / no |
| Source | raw trace address after ordinary coalescing |

The recorder emits this exact request immediately before the pre-existing
`vm_translation.cc:73` assertion.  See
[offending_request.tsv](offending_request.tsv) and the indexed external log.

## D1 — bounded memory-space census

The compact census is in [address_width_by_space.tsv](address_width_by_space.tsv).
Functional LUD reached 2,394 global transactions with a maximum 47-bit SimVA.
BFS functional reached 5,711 global transactions before its first high
address, with maximum width 56.  The disabled and ideal BFS controls each
finished with 49,047 global transactions, 12 at or above 2^49, maximum width
56.  No local or param-local transaction reached the VM hook in these bounded
LUD/BFS runs; this does not generalize beyond the available traces.

## D2 — source proof

The raw active lane at `kernel-7.traceg:1237` carries
`0x00fffdc0000000cd` for `STG.E.SYS` with a nonzero active mask.  Normal
32-byte coalescing yields `0xfffdc0000000c0`, exactly the VM-hook value.
There is no local/generic transformation on this `global_space` path.  The
full code chain and distinct local path are documented in [source_path.md](source_path.md).

## D3 — same-head mode controls

With the identical binary, trace, RTX3070 configuration and one-kernel stream:

- `VM_DISABLED` completed (exit 0) and accepted the same kernel-7/PC-`0x250`
  coalesced `0xfffdc0000000c0` transaction.
- `VM_IDEAL_IDENTITY` completed (exit 0), accepted that same value, and the
  existing identity assertion preserved `SimVA == SimPA`.
- Functional VM reproduced the width-contract assertion at the first captured
  high request.

The detailed comparison is [mode_comparison.tsv](mode_comparison.tsv).  These
controls establish simulator/trace provenance only; they do not establish a
commercial GPU architectural VA-width claim.

The functional run used `/tmp/g3-2-vm-real-small-tlb.config`; the controls
used `/tmp/g3-2a-vm-disabled.config` and `/tmp/g3-2a-vm-ideal.config`, with
the recorder enabled solely by `GPGPUSIM_VM_PROVENANCE_PREFIX`.  Each run was
bounded with `timeout 180s` and a 10GiB virtual-memory limit.  No timeout was
the observed result: functional stopped at the expected assertion, and both
controls exited 0.

## D4 — exclusion checks

The value is not all ones and is not an uninitialized/sentinel artifact: it is
a literal raw trace operand on a real active-lane store and is reproducible in
functional, disabled, and ideal modes.  It is 32B and does not cross a 64KB
page.  Its `GLOBAL_ACC_W` classification and the PTE no-recursion contract
exclude a recursively translated PTE request.  All captured above-49-bit
transactions were classified global; none were local/param-local in this
bounded corpus.

## D5 — classification and required decision

**Classification: Case A — legitimate raw/global SimVA exceeds 49 bits.**

Evidence: a raw BFS global store address produces the matching coalesced SimVA
above 49 bits, and the same numeric transaction completes in disabled and
ideal-identity modes.  “Legitimate” here means a coherent, active,
trace-derived simulator data request; it is deliberately not a claim that this
value proves a generic physical GPU VA contract.

The generic VM address-width/backend contract needs an explicit architecture
decision before any implementation.  A target Segmentation reproduction may
still use its paper-specific 49-bit configuration, but that evidence cannot
silently constrain all Accel-Sim trace SimVA values.  No VA-width change,
masking/truncation/canonicalization, PTE namespace/range change, page-size or
ASID change, translation bypass, stash operation, or G3-3 work was performed.

## Evidence index and stop boundary

Raw external artifacts are indexed in [RAW_LOG_INDEX.tsv](RAW_LOG_INDEX.tsv);
compact in-repository facts are in the TSV files above.  G3-2 remains blocked
pending ChatGPT architecture review.  Core's local G3-2 implementation remains
uncommitted and must not be treated as accepted source.
