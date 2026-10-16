# r3 source, dependencies and final caller hooks

Core producer `ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5` incorporates only the current Lane-1 candidate `10d7f4fea1f9699b4e091091f7e23e072c19d453`, not a merge of historical feature lines. The minimal patch is against that exact public candidate and excludes its WB implementation.

- ep-l2-ro-transactions.h: D512/Line-MSHR ownership, epoch/certificate guard, separate detach and bypass modes, sector state and exact response commit.
- ep-l2-ro-store-port.h: direct binding to the sole ep_l2_payload_store and a tag_port supplied by final l2_cache integration.
- gpu-cache.h/.cc: shared descriptor/native Line-MSHR leases, explicit RO role/status, shared FREE+live accounting and RO bank counters; no new allocator.
- test_ro_store_port.cc: actual common-store/pin/sector/bank service plus a separate immutable version reference and reference Tag view.
- test_ro_transactions.cc, test_ro_oracle_certificate.cc: earlier seven lifecycle scenario groups and input parser/eligibility boundaries.

Final Lane-1 caller responsibilities: classify only original GLOBAL_ACC_R with oracle membership (exclude synthetic WA/atomic/WB), reserve atomically and rollback unused landing on descriptor refusal, instantiate this adapter once per common cache, supply actual Tag generation/handle/address callbacks, route accepted lower transactions and sector returns by handle/generation, dispatch ready responses to L2-to-ICNT with same-cycle commit, preserve detach-only native merge and bypass-mode detached non-coalescing, bind epoch drain/invalidation and verified input loading, register separate default-OFF runtime bits and reject unsupported modes. No caller may reintroduce reserve_resident's address sweep for RO instances.

No full RO performance row is authorized by this module's review-ready label. Lane 5 consumes a qualified integrated release with actual binary/config/trace/run-key identity.
