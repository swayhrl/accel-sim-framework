# G3-5A translation latency accounting

Core `5ba17a1b` records state intervals, not an artificial additive sum across
overlapping/shared events.  A completed requester has an entry timestamp,
L1 launch/completion, optional L2 launch/completion, optional MSHR join, and
READY/wakeup timestamp.  A unique MSHR independently records allocation,
PWQ/walker service, merge depth and lifetime; each physical PTE request records
its own issue-to-response interval.

The counters are counts, total cycles and maxima for requester total, L1 queue
and service, L2 queue and service, requester MSHR wait, and PTE memory wait.
They are critical-path/state intervals: no report adds them as a claim of a
non-overlapping decomposition.  In particular, a PTE response interval is
counted once per physical PTE request, not once per merged requester.

`tests/vm_m3_g3_5_latency_accounting_test.cc` is the machine-checkable proof.
With L1/L2/fixed-walk latency `2/3/20`, requester A enters at 0, joins at 5
and wakes at 25; B enters at 6, joins at 11 and wakes at 25.  The test asserts
totals `25+19`, services `2+2` and `3+3`, MSHR waits `20+14`, one allocation
and one merge.  It separately asserts a 2-cycle L1 hit.  In a real-PTE PWC
case, a related second walk has three intermediate PWC hits, five PTE requests
total, and exactly one deliberately delayed four-cycle PTE-memory interval.

Source anchors: `vm_translation.h` requester/PTE counters at lines 238–308;
lookup state/timestamps at lines 404–473; service and monotonic accounting in
`vm_translation.cc` lines 467–635 and PTE issue/response timestamps in the
same file.  The regression also repaired the pre-existing G3-2 directed test
so every synthetic PTE response occurs at or after its issuance; this is a test
timeline correction, not a VM semantic change.
