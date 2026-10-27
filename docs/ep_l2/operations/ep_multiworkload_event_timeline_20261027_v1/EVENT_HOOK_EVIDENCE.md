# Exact event hook evidence (Core78f4)

Paths below are relative to core/src/gpgpu-sim at commit78f4b59e865b136eede74df74c44c210f5b4ca04. All production endpoints are source-inspected; B header controls call the observer API directly and do not prove each production hook was reached. Main owns real linked fixture coverage.

| File:line | Existing event and added notification | Boundary |
|---|---|---|
| ep-l2-reservation-lifetime.h:211 | Tag mask transition -> TAG_MUTATION | existing cached shadow state, no extra Tag scan |
| ep-l2-reservation-lifetime.h:264,271 | frontend exposure/pressure | cached decision and R; dependency-enabled scope only |
| ep-l2-ro-transactions.h:366-372 | RO_STATE / RO_RETIRE | payload transaction namespace |
| ep-l2-ro-runtime.inc:177-181 | RO_DETACH | payload gen primary; original t.generation auxiliary |
| ep-l2-ro-runtime.inc:318-319 | RO_LOWER_CREATE then MISSQ_ENQUEUE | parent is live original requester, no inferred ancestry |
| ep-l2-ro-runtime.inc:335 | RO_BIND | actual binding |
| ep-l2-ro-runtime.inc:415 | RO_READY | after actual accepted return |
| ep-l2-ft-cache.inc:331-335 | actual production RESERVATION_FAIL | common FT1/FT2 probe result before relieve |
| gpu-cache.cc:1630,1636-1637 | L1_SEND_DENY / L1_SEND / MISSQ_DEQUEUE | actual send success or refusal, not inferred service |
| gpu-cache.cc:1844,1865,1890 | MISSQ_ENQUEUE | original pushes |
| gpu-cache.cc:2574 | FRONTEND_COMMIT | existing FT access result != RESERVATION_FAIL; live mf |
| shader.cc:4724 | ICNT_INJECT | CORE execution endpoint; slice unknown if unavailable |
| l2cache.h:684; l2cache.cc:1731 | LOWER_ENQUEUE | after actual existing FIFO push |
| l2cache.cc:736,834 | DRAM_DELAY_ENQUEUE | original fixed-delay ready-cycle recorded |
| l2cache.cc:854 | DRAM_MC_PUSH | after original actual push; previous deadline retained |
| l2cache.cc:1317 | LOWER_REJECT | demand+full; UID unknown rather than adding peek |
| l2cache.cc:1476-1477 | FRONTEND_WAIT/ADMIT_DECISION, MISSQ_REJECT | cached frontend/admission decision, no new query |
| l2cache.cc:1791 | LOWER_DEQUEUE | existing actual lowerpop |
| l2cache.cc:1856 | DRAM_RETURN | destination return FIFO accepts packet |
| l2cache.cc:2640,2664,2682 | PACKET_SPLIT | actual newly created children, known parent |
| l2cache.cc:2691 | L2_INGRESS | actual packet entering slice |
| l2cache.cc:2818 | RESPONSE_ACCEPT | actual response acceptance |
| dram_sched.cc:228 | SCHEDULER_ACCEPT | after existing scheduler add_req |
| dram.cc:575,611 | DRAM_COLUMN | original real RD/WR column issue |
| gpu-sim.cc:935,1075 | kernel_launch / kernel_finish | finish means CTA/kernel completion, not backend drain |
| gpu-sim.cc:1447-1453 | sentinel LIFE/EPET finalization | stream ~0ULL, inactive, uncapped; idempotent |
| gpu-sim.cc:2153-2155 | geometry and actual clock boundary | before domain actions; preserves global ordinal |

Default OFF does not allocate observer state and adds guarded notification branches. Retained ring/capture storage is bounded, but static initializer footprint, linked ELF size, runtime allocator cost, and real-model timing must be measured separately. No modeled lookup/queue/scheduling operation was intentionally added; textual-operation-site matching is supporting evidence, not a replacement for production OFF/ON comparison.
