# Implementation capacity and metadata delta

Primary data remains 1168×128B per slice (1024+128+16); sensitivity remains 1160×128B. Four banks each serve one line operation/cycle. R0's shared 128B copy latch is unchanged. There is no new data allocator, payload array or D512 descriptor pool.

| State | Actual bound / cost |
|---|---|
| RO completion records | One indexed row per physical payload slot: T_RO=1168 primary / 1160 sensitivity. Live transactions additionally limited by D512; 128 is not this implementation's completion capacity. |
| Completion fields | Canonical line, epoch, payload id/generation, Tag index/generation, required/issued/ready masks, attachment/reuse flags, descriptor waiter links and cycle-local response-grant control. Reuse common fields where possible in a physical design; current C++ fields do not prove a compressed hardware encoding. |
| Waiters | Same shared D512 descriptor allocation; total 512 including native requesters, at most 32 per line including attached and detached transactions. Software waiter vectors reference those leases; they are bounded metadata, not an additional pool of request capacity. |
| Native Line-MSHR | Detach-only retains a real entry in the existing 128-entry index and adds an RO-owner flag + payload handle for that entry. Bypass allocates none for RO. |
| Tag sidecar | Existing payload handle plus a Tag-generation counter per configured Tag (normally 1024/slice). Detached Tag visibility is cleared, old payload stays pinned. |
| Scheduler | Bounded completion selection and native/RO alternating priority. One selected response metadata record (handle, pointer/mask and granted cycle), no response data buffer. |
| Per-address admission credit | Existing shared descriptor guard includes RO lease lines/generations and combined per-address count. Its descriptor comparisons/credit logic must be included in a physical ledger; no free merge CAM is claimed. This guard never returns a detached merge target in bypass mode. |
| Lower packets | One RO-routing bit; existing payload handle, sector mask and symbolic version field. Outstanding sector data stays in existing lower queues until the common bank grants write. |
| Banks | Dedicated RO_FILL_WRITE and RO_RESPONSE_READ operation classes arbitrate in the same banks as R0 hits/fills/WB. Separate counters are observational. |
| Oracle | Shared experimental membership input, offline whole-commandlist certification; manifest/range/commandlist SHA checks run before use. Annotation storage/compiler/runtime support and external-agent assumptions remain explicit costs/limits. |

The earlier r3 bit formula remains an upper-bound starting point with T_RO corrected to the physical slot count. Add Tag-generation state, native RO owner handle, response selector and admission-credit comparison logic, and subtract only line-MSHR fields actually removed. No lower total metadata area, RTL timing, energy or end-to-end speedup is established. Software integer widths, pointers, containers and sizeof are not PPA measurements.
