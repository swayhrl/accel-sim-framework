# Vector F performance cost candidates

Accepted sameSource862 DRAM1700: S45,974,F55,925 cycles (F21.64484% more cycles). This diagnostic service-frequency background is not a calibrated physical GPU result.

Small accepted summaries show S/F both issue1,000,000 lower reads and32,000,000 lower-read bytes. F eliminates117,537 logical copy reads and writes and uses fewer physical bank grants (2,852,611?2,617,269), yet has more cycles. F has250,849 RO transactions and749,151 merges serving1,000,000 RO requests; detached0. RO merge count therefore does not establish lower-traffic savings relative to ordinary S merging/sector behavior.

Actual Victim read responses, dirty-forward responses and served sectors are all zero across the64 emitted slice summaries, despite375,000 directory queries. This is measured zero in this accepted input, not missing statistics filled with zero.

First-wait exposure: S COPY_PIPELINE117,537 and DATA_SERVICE170,160 request-tick sums; F READONLY_LOOKUP1,000,000,VICTIM_LOOKUP375,000,DATA_SERVICE107,612. Any-first-block sums307,312?1,482,612. These are per-request/slice populations and overlapping reasons, not exclusive GPU stall cycles; they cannot be summed/subtracted into the9,951-cycle gap.

Candidate ranking: (1) W/WV decomposition to isolate whether extra package cost arrives with V or RO/M/T; (2) only then prepare finite-port/pipeline candidates for the implicated query path. Existing RO query latency/ports and Victim lookup are modeled hardware work; zeroing them would be a separate diagnostic upper bound, not a bug fix or free hardware optimization. If W itself regresses, inspect allocation/bank-service interaction before blaming RO. No directory/port/protection policy was relaxed.

First-wait counters show zero ordinary line-MSHR/descriptor/MissQ/bank-compatible landing waits. This does not prove these resources never fill. These two proposed applications are the minimum useful discriminator; no new observer or expanded matrix is justified yet.
