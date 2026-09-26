# AI-shaped UVM behavior

Status: `READY_FOR_AI_UVM_CHARACTERIZATION_V1`. Claims apply only to these deterministic synthetic patterns on RTX4080/Linux.

- **P1 dense stream:** R0/R1 demand cold runs migrate approximately the allocation once and repeat becomes resident-fast. At R2/R3, HtoD traffic rises to about 113/129 GB and DtoH eviction to about 96/112 GB; repeat remains about 10/11 s. The full streamed set repeatedly thrashes once it exceeds VRAM.
- **P2 growing prefix:** R0/R1 likewise stabilize after cold placement. R2/R3 produce about 109/123 GB HtoD and 92/107 GB DtoH; repeat remains about 9/11 s. Step data records the monotonic active-prefix transition rather than calling it real attention.
- **P3 sparse expert rotation:** even at R2/R3, only selected expert regions are touched. HtoD is about 8.3/9.4 GB, DtoH about 2 MB, and immediate repeat is about 33/36 ms. It avoids the cyclic whole-pool thrash seen in P1/P2.
- Resident M1 prefetch removes most cold-placement cost. Full prefetch is intentionally not applied under oversubscription.

Migration memcpy telemetry is available and correlated to NVTX steps. Dedicated GPU/CPU page-fault counters are unavailable, so no fault-group count, TLB miss rate, PPN continuity, migration page-size, or shootdown claim is made. Synthetic access laws must not be represented as measured LLM or OLMoE behavior.
