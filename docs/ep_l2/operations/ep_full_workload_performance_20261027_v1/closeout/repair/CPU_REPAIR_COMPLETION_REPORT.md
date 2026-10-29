# Host-write V3 CPU engineering completion

PROVEN: the private V3 family rebuilt all 142 production translation units with O0/g0/final -UNDEBUG. Its eight new archives contain exactly 140 expected, unique members and each member matches its newly compiled object SHA; two additional TUs form the model entry. No old archive was linked. The new model ELF was linked, never executed.

Actual persistent tests: pure protocol 800 checks; eight real 64-slice CPU cache cases covering S/WV default-OFF refusal, flushL1=0 domain refusal, 8000B/250-sector/8-chunk overwrite and pending/drain resume; and two unchanged original host-prefill regression suites on lawful synthetic one-set linear/WBUF16/observer-OFF inputs. S exercises cold lower refill and real dirty WB/WAD/set_done replay; WV exercises unsafe-TVD refusal. Untargeted sectors retain their GPU versions. All ten production cases PASS.

V3 adds a required flushL1=1 boundary to V2: host overwrite cannot make an old upstream L1 copy coherent by only changing L2. No free L1 invalidation was introduced. Supported host writes are aligned complete 32B sectors, ready same-owner L2 residents, drained hardware, T=M=0/no RO, ordinary32x8/P1 resources, no occupied TVD alias and heavy observers OFF. Other cases fail closed.

UNKNOWN: complete nine-kernel particlefilter compatibility, numerical data correctness, native174 application timing/noninterference, Source/parser/host/scientific qualification. Production UID/generation/mask corruption injection was not added; only the pure typed negatives cover those identities. This is a bounded production-component repair, not a restored/accepted application result or T performance gain. The two historical application failures stay unchanged.

All work executed on local WSL CPU. No Trace body, CUDA collection, full application, native budget, registry, accepted Source or old result was altered. Large final assets are destined for the existing Goal namespace on genuine164. Full argument/resource/stdout records preserve setup errors and RAM/FSIZE holds.

The Source is identified by immutable content and patch SHA, not a newly invented or inherited Git commit. Native application use requires an independently registered new Source family and exact fresh authorization.
