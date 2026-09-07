# Weight Segment v1 architecture specification

## Scope and evidence boundary

`PAPER_SPEC`: Weight is read-only and long-lived in inference. The serving framework places it in a
large virtually contiguous buffer. Complete paging bypass requires virtual and physical contiguity.
A descriptor has base/limit/offset semantics. Typical colocated model count is small (roughly 2--8).

`EXISTING_MODEL_FACT`: the frozen C3 implementation stores only range endpoints, gates eligibility
with `OBJECT_WEIGHT`, and returns identity-like `ppn=vpn`. It has no descriptor port or lifecycle.

`C9_MODEL_DECISION`: v1 is a distinct, context-bound, real-PA range translation model. It is not
paper-exact, and it does not infer a model object type in hardware.

## Descriptor semantics and mapping

### Address ABI

| Quantity | v1 value | Label | Meaning |
| --- | ---: | --- | --- |
| byte VA width | 49 | `PAPER_SPEC` + `C9_MODEL_DECISION` | Existing configured VA width; used as model ABI. |
| byte PA width | 49 | `C9_MODEL_DECISION` | Explicit modeled physical-address namespace, parameterized in C10; not a claim about target silicon. |
| base page | 64KiB | `PAPER_SPEC` + `C9_MODEL_DECISION` | v1 segment granularity; low 16 bits are byte offset. |
| VPN/PPN width | 33 | `C9_MODEL_DECISION` | `49 - 16`; PA identity is prohibited even though widths coincide. |
| ASID width | 16 | `C9_MODEL_DECISION` | Required context tag; future config reports it. |
| epoch width | 16 | `C9_MODEL_DECISION` | Nonzero driver-managed generation; wrap requires global quiesce before reuse. |

The internal descriptor range denotes **only full 64KiB pages wholly admitted by the privileged
registration**. An allocation's leading/trailing partial page is deliberately not described by a
descriptor and goes through conventional paging. This prevents page rounding from granting Segment
eligibility to a neighbouring allocation. All eligible transaction bytes must be in one admitted
page; page-crossing requests miss rather than fabricate a Segment hit.

### Required descriptor fields

| Field | Bits | Semantics |
| --- | ---: | --- |
| `valid` | 1 | Set only after all clusters acknowledge installation. |
| `asid` | 16 | Exact active-context identity. |
| `va_base_vpn` | 33 | Inclusive first virtual page of a descriptor extent. |
| `va_limit_vpn` | 33 | Inclusive last virtual page of the same extent. |
| `pa_base_ppn` | 33 | Physical page corresponding to `va_base_vpn`; proves no identity assumption. |
| `read_only` | 1 | Only read accesses may use the bypass; other accesses reject to conventional VM. |
| `mapping_class` | 2 | `00=pinned-contiguous-64KiB`; other encodings are reserved/rejected in v1. |
| `epoch` | 16 | Must equal the active driver epoch for that ASID. |

The descriptor size is:

```
D_v1 = 1 + 16 + 33 + 33 + 33 + 1 + 2 + 16 = 135 bits
```

This is storage accounting only. Comparator inputs, replication wires, update transport, ECC/parity,
array padding and timing closure are not counted. No area/power claim follows.

### Hit predicate and real PA result

For request `(asid, va, bytes, access)`, let `vpn=va>>16`, `offset=va & 0xffff`, and
`request_end=offset+bytes-1`. Exactly one descriptor may match; driver rejects overlap within an
ASID. The predicate is:

```
valid && asid_match && epoch_match && read_only && access==READ &&
mapping_class==PINNED_CONTIGUOUS_64K &&
va_base_vpn <= vpn <= va_limit_vpn && request_end < 65536
```

The output is:

```
ppn = pa_base_ppn + (vpn - va_base_vpn)
pa  = (ppn << 16) | offset
```

`PAPER_SPEC` supplies base/limit/offset. The field widths, full-page admission rule, read-only
predicate and failure policy are `C9_MODEL_DECISION`. `ppn=vpn` is never a legal Segment translation
result unless ordinary arithmetic happens to produce equal numbers. C10 must test a non-identity PA
base explicitly.

## Registration and extent decomposition

`USER_APPROVED_DIRECTION`: non-contiguous allocations split into physical extents. The driver walks
the approved allocation's page mapping, takes maximal runs where consecutive VPNs map to consecutive
PPNs, removes partial endpoint pages, and constructs a descriptor for each remaining run. It checks
ASID ownership, read-only permission, mapping class and pinned status.

`C9_MODEL_DECISION`: v1 registration is all-or-nothing per model/context. If the resulting full-page
extent count is zero, exceeds `N=8`, has an overlap, is non-read-only, cannot be pinned, or cannot be
broadcast atomically, **no descriptor for that registration becomes valid**. Every request then uses
ordinary L1/L2/PTW. No prefix selection, object-map fallback or identity mapping is permitted.

## Topology choice and scaling

Three alternatives were compared:

| Topology | Strength | Limitation | C9 decision |
| --- | --- | --- | --- |
| shared banked table | Storage is not replicated | Needs at least 35 aggregate accept slots/cycle or a modeled central queue; routing/update arbitration grows | Not v1. |
| hierarchical/indexed global table | Better for large `N` | Adds index false positives, bank conflicts and update/search policy | Not v1; potential post-v1 direction. |
| local replicated table | Matches local L1 ingress, deterministic one-port contract, simple immutable-epoch updates | Replicates descriptors to all clusters | **Selected.** |

`EXISTING_MODEL_FACT`: C4 shell has 35 translation/L1 clusters and one L1 lookup port per cluster.
`C9_MODEL_DECISION`: each local Segment table accepts one lookup/cycle, exactly matching that ingress.
There is no nominal Segment queue. Once an L1 scheduler admits a lookup, it issues the local Segment
lookup in the same cycle.

The transparent scaling proxy uses `D_v1=135`, 35 replicas and a per-local lookup compare proxy of
`N*(2*33 + 16 + 16) = 98N` input bits: two range compares, ASID compare, epoch compare. It is not
a PPA result.

| N total slots for one provisioned ASID | local descriptor bits | GPU replica bits (`35*N*135`) | compare-input proxy/local lookup | assessment |
| ---: | ---: | ---: | ---: | --- |
| 1 | 135 | 4,725 | 98 | Fits one contiguous model but no practical multi-extent margin. |
| 4 | 540 | 18,900 | 392 | Covers a few extents/models; modest headroom. |
| 8 | 1,080 | 37,800 | 784 | **Selected nominal v1**: paper-small-count aligned and supports fragmented-but-pinned weights. |
| 16 | 2,160 | 75,600 | 1,568 | Feasible model point but doubles selected state/compare proxy without supplied need. |
| 64 | 8,640 | 302,400 | 6,272 | Requires a banked/hierarchical next design; not assumed to retain v1 latency. |

The selected table has no replacement during an active epoch. `C9_MODEL_DECISION` fixes active
descriptor-context capacity to **one provisioned ASID per local table**. Its eight slots may describe
one model with several extents or several models in that ASID. A simultaneous second ASID uses ordinary
paging rather than evicting/aliasing the live table; a context switch requires the lifecycle protocol.
This bounds v1 replica cost at the values above and keeps ASID comparison as an isolation check. A
multi-ASID resident table is a post-v1 architecture decision, not a free capacity multiplier.

## Correctness boundaries

- `PAPER_SPEC`: Segment hit bypasses conventional paging; L1 may operate in parallel.
- `C9_MODEL_DECISION`: only a fully validated descriptor hit may do so. KV, unknown, stores, atomics,
  partial-page endpoints, mapping-class mismatch, epoch mismatch and table overflow use conventional
  translation.
- A descriptor is an alternate translation cache, not an access-control escape hatch. Failed Segment
  permission never becomes an access grant; ordinary PTE handling decides the final fault.
- If L1 and Segment provide mappings for one request, PPN and effective permission must agree. A
  mismatch is an architectural consistency error, not a winner-selection heuristic.
