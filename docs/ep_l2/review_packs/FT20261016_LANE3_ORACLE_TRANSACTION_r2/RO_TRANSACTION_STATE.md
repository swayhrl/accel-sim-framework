# RO transaction state and resource ownership

Identity is the exact Lane-1 ep_l2::PayloadHandle {payload_id,generation}; transaction records are indexed by physical payload ID, bounded by 1168 primary / 1160 sensitivity. They are completion metadata, not another payload allocator or data array. Tag attachment additionally carries tag index/generation and line identity. Source/response addresses never identify a detached instance.

| Operation | Required state / effect |
|---|---|
| Admit | Valid verified epoch + certified global demand read; pre-reserved live landing and matching Tag; reserve one descriptor from the existing mshr_table free-list; pin landing |
| Attached merge | Shared descriptor, combined per-address cap 32, required sector mask extended; reuse_seen permanently protects waiter-aware detachment |
| Lower accept | Set issued bits only after real lower acceptance; never retire descriptor or landing |
| Detach | With Tag-detach enabled and no observed reuse, remove only matching Tag visibility, retain transaction/landing/reference and all masks |
| Detached same-line arrival, bypass ON | New handle/new transaction/lower read; old instance remains alive; concurrent duplicate sector bytes counted |
| Detached same-line arrival, bypass OFF | Lookup/merge through retained native Line-MSHR; no duplicate transaction; native 128-entry capacity enforced |
| Fill | Exactly expected issued sectors; shared bank write; attached matching generation updates current Tag; detached fill never installs a Tag |
| Response | All requested sectors ready, shared bank read; descriptor remains live through FIFO backpressure; successful enqueue commit frees exactly that descriptor |
| Retire | All required sectors issued/ready, all waiters committed, no prepared read reference; unpin; detached releases landing, attached retains clean resident data |
| Epoch end | Refuses until every transaction drains; no force-discard of fills or descriptors |

Tag-detach and Line-MSHR-bypass are separate default-OFF switches. Four combinations are defined: both OFF falls back; detach-only holds native Line-MSHR; bypass-only pins attached Tag; both ON permits detached duplicates. The module does not register or enable a simulator runtime switch before the Lane-1 adapter is executable.

Response reads are cycle-local grants. A failed FIFO enqueue retains ownership and rereads via arbitration on retry; no implicit unbudgeted response-data array is supplied. Caller must commit successful response in its granted cycle. Fill and response data accesses compete with all other roles through the payload_port adapter.

Additional metadata is explicitly real: at most one completion record per physical payload, up to 512 globally shared descriptors, Tag binding, required/issued/ready four-bit masks, reuse_seen/attachment state, waiter links and checked generations. The descriptor hook adds an external-owner bit, canonical line and generation in software. A final physical-bit implementation must report actual line/address widths, bounded generation strategy and reuse/union with existing descriptor fields. This candidate does not claim an equal-metadata-area speedup merely by avoiding Line-MSHR allocation.

## r2 correctness additions

Admission AND merge require membership in a bound runtime oracle_certificate, a matching epoch and an original demand-read class. An epoch writer to a certified line is rejected even if its earlier transaction has retired. Initial resident-ready sectors are preserved on sector misses; only missing unissued sectors issue lower reads. A descriptor cannot be leased twice for the same live request pointer. commit_response receives the actual cycle and refuses a successful enqueue without a same-cycle data read grant. Thirty-two detached same-address objects are tested under the combined per-line cap; reversed fills retire exactly once.
