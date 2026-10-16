# Lane 3 shared-store adapter r3

Candidate source: Core `ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5` against published Lane-1 production candidate `10d7f4fea1f9699b4e091091f7e23e072c19d453` and Framework interface publication `528dd5664cdbf1851e090e049401b10a264de499`. This is a new dependent integration stage; r1/r2 remain immutable.

The RO module now executes landing ownership, pin/unpin, pending-sector retirement, shared-bank fill/response service and handle release against the actual sole ep_l2_payload_store. An explicit RO primary role distinguishes attached/detached pending state; it is included exactly once in FREE+live accounting. Equal-address RO owners survive independently; no address cleanup is used. All-ready attached data becomes RESIDENT, with waiter pins retaining references until actual response commit.

The new test drives the real store and shared mshr_table with an independent sector-version reference. A genuine competing WB bank grant blocks RO fill, return packets remain with their caller on a denial, response backpressure retains the landing, and an old detached response cannot modify the new attached Tag reference. C8/C16 are recognized; static/non-unified construction rejects RO. Dedicated RO bank counters avoid mislabeling RO response reads as native resident hits.

Remaining final integration is Lane 1's actual tag_array generation/visibility callback and cache/memport dispatch, epoch/preflight loader and separate default-OFF runtime config registration. The module does not enable a simulator RO mode or claim full-workload correctness/speedup. Lane 5 independently verifies the final public-Core release and owns formal run allocation.

The five complete input manifests/coverage/exclusions are reused exactly from `../FT20261016_LANE3_ORACLE_TRANSACTION_r2/`; no trace or scientific CSV was changed or rerun. Input producer is d2ba33bd..., verifier source 28a594c7.... Coverage refers to traced global-read lane references, not L2 misses.

See RO_TRANSACTION_STATE.md, SOURCE_MAP.md, RO_READY_MANIFEST.json, patch/ and validation/.

## Executed validation

Seven RO lifecycle reference groups, runtime certificate tests and the actual shared-store version/bank/pin test pass on this exact source. Complete Release build and all eight inherited public-WBUF production regression groups pass under a Lane-5 lease, which is released. Patch applies cleanly to the exact Lane-1 candidate. No formal simulation or performance experiment was launched.
