# C12 required fair-comparison analysis

Labels: `MEASURED_FULL_ROI_FACT`, `SPECULATIVE_CANDIDATE`, `REFERENCE_APPROX_SUBENTRY_16`.

All percentages are the compared-point value divided by the named reference minus one. Cycles/IPC are reported with the raw counters; formal speedup remains same-ROI F0 only.

## MEASURED_FULL_ROI_FACT

### prefill: F1 versus F2

Compared point: `prefill F1 Lseg=NONE` against `prefill F2 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 63302886 | 63758501 | +0.720% |
| gpu_tot_ipc | 291.4973 | 289.4143 | -0.715% |
| vm_l2_tlb_misses | 116873 | 148449 | +27.017% |
| vm_l2_tlb_port_stalls | 1280363 | 1490275 | +16.395% |
| vm_translation_mshr_allocations | 41488 | 49809 | +20.056% |
| vm_translation_mshr_full_events | 0 | 0 | 0.000% |
| vm_translation_walk_starts | 41488 | 49809 | +20.056% |
| vm_pwc_misses | 89 | 117 | +31.461% |
| vm_pte_requests | 41577 | 49926 | +20.081% |
| vm_pte_dram_responses | 27197 | 33837 | +24.414% |
| vm_pte_memory_wait_cycles_total | 17554143 | 20429518 | +16.380% |
| vm_translation_requester_latency_cycles_total | 1078177799 | 1090127446 | +1.108% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=33216 | kernel_records=33216 |
| l2_summary | kernel_records=33216 | kernel_records=33216 |
| l2_queue_summary | kernel_records=692 | kernel_records=692 |
| native_memory_latency_summary | averagemflatency=747;avg_icnt2mem_latency=375;avg_mrq_latency=53;avg_icnt2sh_latency=7 | averagemflatency=762;avg_icnt2mem_latency=385;avg_mrq_latency=54;avg_icnt2sh_latency=7 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### prefill: F5 versus F0

Compared point: `prefill F5 Lseg=NONE` against `prefill F0 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 62490238 | 63223313 | +1.173% |
| gpu_tot_ipc | 295.2881 | 291.8642 | -1.160% |
| vm_l2_tlb_misses | 45227 | 115020 | +154.317% |
| vm_l2_tlb_port_stalls | 935987 | 1293532 | +38.200% |
| vm_translation_mshr_allocations | 20816 | 39171 | +88.177% |
| vm_translation_mshr_full_events | 0 | 0 | 0.000% |
| vm_translation_walk_starts | 20816 | 39171 | +88.177% |
| vm_pwc_misses | 83 | 88 | +6.024% |
| vm_pte_requests | 20899 | 39259 | +87.851% |
| vm_pte_dram_responses | 8629 | 24520 | +184.158% |
| vm_pte_memory_wait_cycles_total | 8161497 | 16290147 | +99.598% |
| vm_translation_requester_latency_cycles_total | 1050434230 | 1076246205 | +2.457% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=33216 | kernel_records=33216 |
| l2_summary | kernel_records=33216 | kernel_records=33216 |
| l2_queue_summary | kernel_records=692 | kernel_records=692 |
| native_memory_latency_summary | averagemflatency=745;avg_icnt2mem_latency=375;avg_mrq_latency=53;avg_icnt2sh_latency=7 | averagemflatency=745;avg_icnt2mem_latency=374;avg_mrq_latency=53;avg_icnt2sh_latency=7 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### prefill: F7 Lseg=10 versus F0

Compared point: `prefill F7 Lseg=10` against `prefill F0 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 62490238 | 63370888 | +1.409% |
| gpu_tot_ipc | 295.2881 | 291.1845 | -1.390% |
| vm_l2_tlb_misses | 45227 | 120919 | +167.360% |
| vm_l2_tlb_port_stalls | 935987 | 1234186 | +31.859% |
| vm_translation_mshr_allocations | 20816 | 33749 | +62.130% |
| vm_translation_mshr_full_events | 0 | 0 | 0.000% |
| vm_translation_walk_starts | 20816 | 33749 | +62.130% |
| vm_pwc_misses | 83 | 23 | -72.289% |
| vm_pte_requests | 20899 | 33772 | +61.596% |
| vm_pte_dram_responses | 8629 | 29715 | +244.362% |
| vm_pte_memory_wait_cycles_total | 8161497 | 15277922 | +87.195% |
| vm_translation_requester_latency_cycles_total | 1050434230 | 1073767415 | +2.221% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=33216 | kernel_records=33216 |
| l2_summary | kernel_records=33216 | kernel_records=33216 |
| l2_queue_summary | kernel_records=692 | kernel_records=692 |
| native_memory_latency_summary | averagemflatency=745;avg_icnt2mem_latency=375;avg_mrq_latency=53;avg_icnt2sh_latency=7 | averagemflatency=806;avg_icnt2mem_latency=427;avg_mrq_latency=55;avg_icnt2sh_latency=8 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### prefill: F8 Lseg=10 versus F9

Compared point: `prefill F8 Lseg=10` against `prefill F9 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 63252745 | 63375503 | +0.194% |
| gpu_tot_ipc | 291.7284 | 291.1633 | -0.194% |
| vm_l2_tlb_misses | 116249 | 119328 | +2.649% |
| vm_l2_tlb_port_stalls | 1310981 | 1229061 | -6.249% |
| vm_translation_mshr_allocations | 39360 | 33845 | -14.012% |
| vm_translation_mshr_full_events | 0 | 0 | 0.000% |
| vm_translation_walk_starts | 39360 | 33845 | -14.012% |
| vm_pwc_misses | 95 | 22 | -76.842% |
| vm_pte_requests | 39455 | 33867 | -14.163% |
| vm_pte_dram_responses | 24595 | 29682 | +20.683% |
| vm_pte_memory_wait_cycles_total | 16319521 | 15084189 | -7.570% |
| vm_translation_requester_latency_cycles_total | 1076912891 | 1071569405 | -0.496% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=33216 | kernel_records=33216 |
| l2_summary | kernel_records=33216 | kernel_records=33216 |
| l2_queue_summary | kernel_records=692 | kernel_records=692 |
| native_memory_latency_summary | averagemflatency=747;avg_icnt2mem_latency=375;avg_mrq_latency=53;avg_icnt2sh_latency=7 | averagemflatency=806;avg_icnt2mem_latency=428;avg_mrq_latency=55;avg_icnt2sh_latency=7 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### prefill: F8 Lseg=10 versus F1

Compared point: `prefill F8 Lseg=10` against `prefill F1 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 63758501 | 63375503 | -0.601% |
| gpu_tot_ipc | 289.4143 | 291.1633 | +0.604% |
| vm_l2_tlb_misses | 148449 | 119328 | -19.617% |
| vm_l2_tlb_port_stalls | 1490275 | 1229061 | -17.528% |
| vm_translation_mshr_allocations | 49809 | 33845 | -32.050% |
| vm_translation_mshr_full_events | 0 | 0 | 0.000% |
| vm_translation_walk_starts | 49809 | 33845 | -32.050% |
| vm_pwc_misses | 117 | 22 | -81.197% |
| vm_pte_requests | 49926 | 33867 | -32.166% |
| vm_pte_dram_responses | 33837 | 29682 | -12.279% |
| vm_pte_memory_wait_cycles_total | 20429518 | 15084189 | -26.165% |
| vm_translation_requester_latency_cycles_total | 1090127446 | 1071569405 | -1.702% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=33216 | kernel_records=33216 |
| l2_summary | kernel_records=33216 | kernel_records=33216 |
| l2_queue_summary | kernel_records=692 | kernel_records=692 |
| native_memory_latency_summary | averagemflatency=762;avg_icnt2mem_latency=385;avg_mrq_latency=54;avg_icnt2sh_latency=7 | averagemflatency=806;avg_icnt2mem_latency=428;avg_mrq_latency=55;avg_icnt2sh_latency=7 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### prefill: F7 Lseg sensitivity (L5 / L10 / L20)

| Lseg | cycles | same-ROI F0 speedup | Segment attempts | Segment hits | Segment L2 suppressed |
|---:|---:|---:|---:|---:|---:|
| 5 | 59834219 | 1.044389633 | 96085613 | 49633881 | 49633881 |
| 10 | 63370888 | 0.986103240 | 94194188 | 48092734 | 48092734 |
| 20 | 76131192 | 0.820823060 | 93915052 | 47926636 | 47926636 |

### prefill: F8 Lseg sensitivity (L5 / L10 / L20)

| Lseg | cycles | same-ROI F0 speedup | Segment attempts | Segment hits | Segment L2 suppressed |
|---:|---:|---:|---:|---:|---:|
| 5 | 59817355 | 1.044684072 | 96116757 | 49654479 | 49654479 |
| 10 | 63375503 | 0.986031432 | 94191864 | 48091640 | 48091640 |
| 20 | 76144277 | 0.820682006 | 93916855 | 47926888 | 47926888 |

### decode1: F1 versus F2

Compared point: `decode1 F1 Lseg=NONE` against `decode1 F2 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 34564626 | 34540487 | -0.070% |
| gpu_tot_ipc | 119.4444 | 119.5279 | +0.070% |
| vm_l2_tlb_misses | 22220 | 21202 | -4.581% |
| vm_l2_tlb_port_stalls | 309614 | 299499 | -3.267% |
| vm_translation_mshr_allocations | 15691 | 15617 | -0.472% |
| vm_translation_mshr_full_events | 135022 | 132023 | -2.221% |
| vm_translation_walk_starts | 15691 | 15617 | -0.472% |
| vm_pwc_misses | 105 | 88 | -16.190% |
| vm_pte_requests | 15796 | 15705 | -0.576% |
| vm_pte_dram_responses | 4134 | 4104 | -0.726% |
| vm_pte_memory_wait_cycles_total | 7337292 | 7538059 | +2.736% |
| vm_translation_requester_latency_cycles_total | 775156250 | 775031124 | -0.016% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=35520 | kernel_records=35520 |
| l2_summary | kernel_records=35520 | kernel_records=35520 |
| l2_queue_summary | kernel_records=740 | kernel_records=740 |
| native_memory_latency_summary | averagemflatency=1258;avg_icnt2mem_latency=793;avg_mrq_latency=52;avg_icnt2sh_latency=2 | averagemflatency=1245;avg_icnt2mem_latency=781;avg_mrq_latency=52;avg_icnt2sh_latency=2 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### decode1: F5 versus F0

Compared point: `decode1 F5 Lseg=NONE` against `decode1 F0 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 34564626 | 34558846 | -0.017% |
| gpu_tot_ipc | 119.4444 | 119.4644 | +0.017% |
| vm_l2_tlb_misses | 22220 | 22128 | -0.414% |
| vm_l2_tlb_port_stalls | 309614 | 309708 | +0.030% |
| vm_translation_mshr_allocations | 15691 | 15691 | +0.000% |
| vm_translation_mshr_full_events | 135022 | 139758 | +3.508% |
| vm_translation_walk_starts | 15691 | 15691 | +0.000% |
| vm_pwc_misses | 105 | 95 | -9.524% |
| vm_pte_requests | 15796 | 15786 | -0.063% |
| vm_pte_dram_responses | 4134 | 4129 | -0.121% |
| vm_pte_memory_wait_cycles_total | 7337292 | 7376887 | +0.540% |
| vm_translation_requester_latency_cycles_total | 775156250 | 775122973 | -0.004% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=35520 | kernel_records=35520 |
| l2_summary | kernel_records=35520 | kernel_records=35520 |
| l2_queue_summary | kernel_records=740 | kernel_records=740 |
| native_memory_latency_summary | averagemflatency=1258;avg_icnt2mem_latency=793;avg_mrq_latency=52;avg_icnt2sh_latency=2 | averagemflatency=1254;avg_icnt2mem_latency=789;avg_mrq_latency=52;avg_icnt2sh_latency=2 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### decode1: F7 Lseg=10 versus F0

Compared point: `decode1 F7 Lseg=10` against `decode1 F0 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 34564626 | 34432059 | -0.384% |
| gpu_tot_ipc | 119.4444 | 119.9043 | +0.385% |
| vm_l2_tlb_misses | 22220 | 2405 | -89.176% |
| vm_l2_tlb_port_stalls | 309614 | 167686 | -45.840% |
| vm_translation_mshr_allocations | 15691 | 170 | -98.917% |
| vm_translation_mshr_full_events | 135022 | 0 | -100.000% |
| vm_translation_walk_starts | 15691 | 170 | -98.917% |
| vm_pwc_misses | 105 | 13 | -87.619% |
| vm_pte_requests | 15796 | 183 | -98.841% |
| vm_pte_dram_responses | 4134 | 104 | -97.484% |
| vm_pte_memory_wait_cycles_total | 7337292 | 113647 | -98.451% |
| vm_translation_requester_latency_cycles_total | 775156250 | 763442534 | -1.511% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=35520 | kernel_records=35520 |
| l2_summary | kernel_records=35520 | kernel_records=35520 |
| l2_queue_summary | kernel_records=740 | kernel_records=740 |
| native_memory_latency_summary | averagemflatency=1258;avg_icnt2mem_latency=793;avg_mrq_latency=52;avg_icnt2sh_latency=2 | averagemflatency=1285;avg_icnt2mem_latency=833;avg_mrq_latency=55;avg_icnt2sh_latency=2 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### decode1: F8 Lseg=10 versus F9

Compared point: `decode1 F8 Lseg=10` against `decode1 F9 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 34564626 | 34432059 | -0.384% |
| gpu_tot_ipc | 119.4444 | 119.9043 | +0.385% |
| vm_l2_tlb_misses | 22220 | 2405 | -89.176% |
| vm_l2_tlb_port_stalls | 309614 | 167686 | -45.840% |
| vm_translation_mshr_allocations | 15691 | 170 | -98.917% |
| vm_translation_mshr_full_events | 135022 | 0 | -100.000% |
| vm_translation_walk_starts | 15691 | 170 | -98.917% |
| vm_pwc_misses | 105 | 13 | -87.619% |
| vm_pte_requests | 15796 | 183 | -98.841% |
| vm_pte_dram_responses | 4134 | 104 | -97.484% |
| vm_pte_memory_wait_cycles_total | 7337292 | 113647 | -98.451% |
| vm_translation_requester_latency_cycles_total | 775156250 | 763442534 | -1.511% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=35520 | kernel_records=35520 |
| l2_summary | kernel_records=35520 | kernel_records=35520 |
| l2_queue_summary | kernel_records=740 | kernel_records=740 |
| native_memory_latency_summary | averagemflatency=1258;avg_icnt2mem_latency=793;avg_mrq_latency=52;avg_icnt2sh_latency=2 | averagemflatency=1285;avg_icnt2mem_latency=833;avg_mrq_latency=55;avg_icnt2sh_latency=2 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### decode1: F8 Lseg=10 versus F1

Compared point: `decode1 F8 Lseg=10` against `decode1 F1 Lseg=NONE`.

| Observable | reference | compared point | compared/reference change |
|---|---:|---:|---:|
| gpu_tot_sim_cycle | 34540487 | 34432059 | -0.314% |
| gpu_tot_ipc | 119.5279 | 119.9043 | +0.315% |
| vm_l2_tlb_misses | 21202 | 2405 | -88.657% |
| vm_l2_tlb_port_stalls | 299499 | 167686 | -44.011% |
| vm_translation_mshr_allocations | 15617 | 170 | -98.911% |
| vm_translation_mshr_full_events | 132023 | 0 | -100.000% |
| vm_translation_walk_starts | 15617 | 170 | -98.911% |
| vm_pwc_misses | 88 | 13 | -85.227% |
| vm_pte_requests | 15705 | 183 | -98.835% |
| vm_pte_dram_responses | 4104 | 104 | -97.466% |
| vm_pte_memory_wait_cycles_total | 7538059 | 113647 | -98.492% |
| vm_translation_requester_latency_cycles_total | 775031124 | 763442534 | -1.495% |

Cache / queue / memory summaries (preserved verbatim; interpret only with the numeric translation counters above):

| Layer | reference | compared point |
|---|---|---|
| l1d_summary | kernel_records=35520 | kernel_records=35520 |
| l2_summary | kernel_records=35520 | kernel_records=35520 |
| l2_queue_summary | kernel_records=740 | kernel_records=740 |
| native_memory_latency_summary | averagemflatency=1245;avg_icnt2mem_latency=781;avg_mrq_latency=52;avg_icnt2sh_latency=2 | averagemflatency=1285;avg_icnt2mem_latency=833;avg_mrq_latency=55;avg_icnt2sh_latency=2 |

Interpretation boundary: this is a measured association across TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and memory observables; it does not alone establish a unique causal bottleneck.

### decode1: F7 Lseg sensitivity (L5 / L10 / L20)

| Lseg | cycles | same-ROI F0 speedup | Segment attempts | Segment hits | Segment L2 suppressed |
|---:|---:|---:|---:|---:|---:|
| 5 | 33959029 | 1.017833166 | 76449032 | 8430211 | 8430211 |
| 10 | 34432059 | 1.003850104 | 76027483 | 8053776 | 8053776 |
| 20 | 36035731 | 0.959176491 | 75820504 | 7922297 | 7922297 |

### decode1: F8 Lseg sensitivity (L5 / L10 / L20)

| Lseg | cycles | same-ROI F0 speedup | Segment attempts | Segment hits | Segment L2 suppressed |
|---:|---:|---:|---:|---:|---:|
| 5 | 33959029 | 1.017833166 | 76449032 | 8430211 | 8430211 |
| 10 | 34432059 | 1.003850104 | 76027483 | 8053776 | 8053776 |
| 20 | 36035731 | 0.959176491 | 75820504 | 7922297 | 7922297 |

## Prefill versus Decode1

Absolute cycles are not cross-ROI comparable because Prefill and Decode1 have different immutable kernel lists. This table compares each arm's *same-ROI F0-normalized* speedup and preserves the relevant translation signal.

| arm | lseg | Prefill speedup vs Prefill F0 | Decode1 speedup vs Decode1 F0 | Prefill L2 TLB misses | Decode1 L2 TLB misses | Prefill PTE requests | Decode1 PTE requests |
|---|---|---:|---:|---:|---:|---:|---:|
| F0 | NONE | 1.000000000 | 1.000000000 | 45227 | 22220 | 20899 | 15796 |
| F1 | NONE | 0.980108331 | 1.000698861 | 148449 | 21202 | 49926 | 15705 |
| F2 | NONE | 0.987162544 | 1.000000000 | 116873 | 22220 | 41577 | 15796 |
| F5 | NONE | 0.988404989 | 1.000167251 | 115020 | 22128 | 39259 | 15786 |
| F7 | 10 | 0.986103240 | 1.003850104 | 120919 | 2405 | 33772 | 183 |
| F7 | 20 | 0.820823060 | 0.959176491 | 119458 | 2659 | 33773 | 182 |
| F7 | 5 | 1.044389633 | 1.017833166 | 118222 | 2450 | 33773 | 182 |
| F8 | 10 | 0.986031432 | 1.003850104 | 119328 | 2405 | 33867 | 183 |
| F8 | 20 | 0.820682006 | 0.959176491 | 118774 | 2659 | 33689 | 182 |
| F8 | 5 | 1.044684072 | 1.017833166 | 123208 | 2450 | 47985 | 182 |
| F9 | NONE | 0.987945077 | 1.000000000 | 116249 | 22220 | 39455 | 15796 |

## SUPPORTED_MECHANISM_SIGNAL

The tables intentionally require concordant variation in TLB, MSHR/PTW/PWC/PTE, requester and cache/queue/memory observables before describing a mechanism signal. They do not treat a miss-rate, IPC, queue, or Segment counter in isolation as causal proof.

## UNRESOLVED

`REFERENCE_APPROX_SUBENTRY_16` remains a reference approximation. `SPECULATIVE_CANDIDATE` and `MODELED_DRIVER_PA` remain modeled simulator constructs, not a proof of a fabricated hardware PPA or of real-hardware PA behavior.
