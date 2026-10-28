No confirmed current RAM-accounting or CPU2 coupling defect was found. No change is needed now.

14 live models and15 pending were independently observed. Host MemAvailable=120.66GiB; cgroup effective headroom=100.84GiB. The95%/10GiB policy allows86.30GiB future growth; existing reservations consume81.43GiB, leaving4.87GiB. Lavamd needs its full81.18GiB; the funding gap is76.31GiB. R is an admission-priority fence and is not charged as another RAM reservation.

| Running program | Jobs | RSS GiB | Anonymous PSS GiB | Future reserve GiB |
|---|---:|---:|---:|---:|
| SYRK | 6 | 54.01 | 53.99 | 30.40 |
| cutcp | 2 | 26.51 | 26.50 | 6.12 |
| hybridsort | 6 | 42.19 | 42.17 | 43.53 |

Peer future reservation=0. The original unresolved scanM16 keeps1.392GiB. Every own envelope/RSS arithmetic check matches and no cohort is duplicated. Six SYRK runs have only failed lower-bound history; current9.12GiB high-waterRSS already exceeds the old9.066GiB failed peak, so reducing their14.068GiB forecast is unsupported. HYBRIDSORT has real completed11.593GiB peak history; current smallerRSS does not prove later growth absent. Remaining work:9lavamd@81.178GiB,2hybridsort@14.287GiB,4SYRK@14.068GiB. Successful historical max walltimes are6.49h/lavamd and13.27h/hybridsort; SYRK has no successful duration, so0 means unknown. These are planning references, not ETA guarantees.

The256GiB cgroup contains148.33GiB anon and22.69GiB file, including18.97GiB inactive_file; dirty=0.000118GiB, writeback=0. Raw cgroup headroom is83.85GiB; the provider already credits16.95GiB clean inactive file. Reclaiming already credited pages lowers current and credit together, so it does not create another equal admission allowance. There is no proof these are exclusive completed DTC-input pages. Global/shared reclaim could affect another Lane or cause164 refault reads. Even the invalid optimistic assumption that all file cache is reclaimable adds at most5.74GiB beyond existing credit, far below the Lavamd gap. No reclaim/drop_caches/fadvise was performed.

Cgroup CPU use was20.98/384cores, with0throttling/OOM-event increments and no current CPU/memory/IO pressure gate. All14 model PID generations advanced CPU ticks. Per-PID CPU_cores in RAW are NOT used: serial smaps reads make the shared global denominator unequal to each PID interval; they are not utilization/inefficiency evidence. Known owner+ancestors use about2.43GiB anonymousPSS; no obvious large DTC-supervisor RAM leak was observed.

Even a non-authorized arithmetic20%->10% successful-history padding reduction would save only10.61GiB for current eligible-shape rows and still leave65.70GiB missing for full-cost lavamd. This is not a safety certificate or recommendation. Natural own drain can conditionally fund2lavamd slots with unchanged full forecasts;3full costs exceed even an otherwise-empty256GiB cgroup95%/10GiB budget.

SIGSTOP keeps already allocated anonymous RAM. Current native supervision rejects stale producer/resource evidence after30s and no retirement after600s; long pauses are not compatible without a separately qualified observation contract. No registered memory-releasing checkpoint is available in this entry chain. Freezing jobs could defer them for roughly a6.49h lavamd run or longer, while not releasing theirRSS. A10GiB visible margin is not a proven allocator-burst/reaction guarantee. No pause, checkpoint, restart, process signal, forecast/budget/source/registry change or test was performed.

Traceable evidence: READONLY_REVIEW.json, READONLY_RESOURCE_EVIDENCE.json and KNOWN_OWNER_ANCESTOR_MEMORY.json. Individual file observations are not one global transaction; fresh snapshots differ from earlier20:58 readings.
