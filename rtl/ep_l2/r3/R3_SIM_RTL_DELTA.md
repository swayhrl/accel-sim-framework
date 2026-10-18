# R3 versus R2 and finite SIM

Candidate A adds no pipeline/register stage, queue, cycle, II or service-order
change. Two independently computed GEN updates retain frontend/lower concurrency
and same-slot lower priority. Phase-shared transaction GEN read replaces
p_landing/p_old/free_staging ports; native_gen outside native_commit may differ
and is unconsumed by the existing interface. All valid-qualified data and every
control are cycle-equivalence targets. No accepted latency/throughput difference
is hidden by that explicit invalid-data qualification.

R2 gaps remain readII4/writeII3, static copy serialization, synchronous assumed
SRAM return, WB holding phases, round-robin rather than SIM oldest arbitration,
and held native approval. Exact finite SIM specification Core9bd30ed9,
Framework8ab6013ea9, producerbinaryfb674... remains specification only.
No SIM source/application/result was changed or started. Unknown146KiB SRAM
and native Tag/LRU/MSHR/dirty-byte/NoC implementation cost remain UNKNOWN.
Any later candidate that changes cycle/II must be isolated and sent to Lane1;
no current performance/area or targetGPU PPA pairing is authorized.

Final qualification addendum: both A/ac607 and B/e8 passed the complete required finite full-size suites; all base/boundary counters and cycles match frozenR2. B only replaces fill-owner identity under the legal ownership invariant; static fixed mapping is hardwired, dynamic forward lookup paid. No new stage/II/order/ownership lifetime change. These finite observations and conditional proofs are not a global equivalence proof or a new officialSIM performance validation. All clocks remain unclosed; unknown macro/native costs remain.
