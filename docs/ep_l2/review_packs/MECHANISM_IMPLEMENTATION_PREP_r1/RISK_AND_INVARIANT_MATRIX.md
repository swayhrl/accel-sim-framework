# Risk and Invariant Matrix

| risk | trigger/source | invariant / detection | gate |
|---|---|---|---|
| stale fill corrupts reused slot | fill after replacement | handle owner+generation+pending sectors match before fill | directed late-fill test; assert at `l2_cache::fill` |
| double free / leak | rollback, replacement, terminal drain | exactly one live owner; release invalidates generation; all queues/slots drain | allocator audit + terminal `EPL2B0V1`/new checks |
| static-mode drift | M1 refactor | static resident/bypass counts 1024/128; same payload IDs/bank mapping | counter/cycle equivalence test |
| bank timing drift | global-ID conversion | `bank=payload_id%4`, oldest-ready retries unchanged | same-bank directed arbitration replay |
| bypass starvation/deadlock | fully shared M2 allocation | protected capacity for live/pending bypass demand; no pending response requires an unavailable slot | exhaust-resident then bypass completion test |
| hidden extra storage | TVD data copied into WAD | live resident + bypass + TVD payload entries <=1152; report bytes/bits | storage-accounting assertion |
| MSHR semantic loss | RO early release | all masks, descriptor lifetime, response enqueue and ordering retained | writes/atomics/order/sector response tests |
| telemetry overclaim | retry counted as blocked cycle | only exact queue-head admission decision increments cycle metrics; field contracts name denominator | OFF equivalence + unit event/cycle tests |
| dormant bypass mistaken for opportunity | current source has no bypass caller | mark unknown until candidate consumer defined | reviewer gate before M2 |
| baseline/mechanism confounded | opaque mode number or branch-specific binary | calibrated resources are a separate config layer; all feature bits OFF is accepted parent baseline | same SHA/binary OFF-vs-parent equivalence |
| accidental experimental default | omitted/unknown option | all feature bits default zero; parser rejects unsupported combination | config parser unit tests |
| mode provenance missing/colliding | runner infers mode from filenames or shares results directory | manifest records base ID/config hash/feature vector and root includes mode | pre-launch manifest duplicate audit |
