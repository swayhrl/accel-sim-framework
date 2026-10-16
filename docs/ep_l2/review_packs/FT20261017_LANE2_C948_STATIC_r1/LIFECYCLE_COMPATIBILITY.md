# c948 compatibility — unchanged mechanism scope

Lane1's62→c948 delta changes only the duplicate observer and direct WBUF test clock. It does not change the later-quiescent clean host-prefill scientific scope, native Tag time, physical bank clock, sole allocator, copy latch, WAD/D512 budgets or lower producers.

Lane2's production TVD adapter bytes remain unchanged from cbdf: shared mandatory WAD occupancy guards host try-prefill, all refusals precede exact optional-alias reclaim/Tag/allocator mutation, owner/pin/pending/generation and same-bank landing are checked; native Tag/full-width host address semantics and actual selected-index assertion remain. WB_STAGED reads wait for actual lower acceptance, WB_INFLIGHT valid reads forward before generic WAD denial, writes/atomic/missing sectors wait; real ICNT lease commit and lower_accept/set_done/epoch cleanup retain physical time. These remain source-scoped evidence until the new integrated runtime is built and validated.

Getter-only patches from previous revisions are retired for this base and must not be reapplied. The corrected direct fixture is imported exactly, not retested as a C++ PASS. New source is not an R0.1 official binary and does not inherit old module or application qualification. Feature flags remain OFF by default. No protocol/budget/oracle/trace/physical port change is introduced.
