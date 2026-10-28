Current DTC memory: independent read-only check

Snapshot 2026-10-28T00:03:53.157189+00:00 (08:03:53 CST), one fresh measurement; not a sustained
OOM/PSI trend study. 16 real live generations and one unresolved old scan M16
reservation are retained. UUID/PID/start identities were checked against the
native records and /proc; lifetime VmHWM values are included per live row.
The unresolved 1.392GiB is not released. Peer RAM entries and claim list are empty
in this snapshot, so growth is the complete own-row sum, not a missing peer credit.

Host MemAvailable is 78.644GiB. Cgroup max=256GiB,
current=198.081GiB, raw headroom=57.919GiB.
The original provider already adds 17.501GiB certified clean
inactive-file credit, producing 75.421GiB effective headroom.
Do not add that credit a second time or treat all host free RAM as admission space.

On the identical sample and unchanged full growth 52.980GiB, old .88/floor8
budget=59.330GiB; new .95/floor10 budget=62.150GiB. The legal increase is
2.819GiB, not an extra copy of the entire new budget. New remaining slack
is 9.170GiB. The cheapest remaining full forecast is scalarProd at
11.494GiB, still 2.324GiB short before CPU/priority/second-fresh
checks. Existing .95 scope is FINITE_CANARY; this numerical global comparison
is not authority to apply .95 outside its allowlist. B5 certified discount is zero.
No immediately removable duplicate, arithmetic bug or presently authorized
forecast reduction was found. Live Lava DH-P0 has about 66.49GiB current RSS,
66.51GiB VmHWM, and retains its full 81.18GiB forecast, not a tail-flat assumption.

Memory/IO PSI full avg10=0, CPU full avg10=0, cgroup oom/oom_kill=0 and CPU
nr_throttled=0. Host oom_kill=366 is a cumulative system counter, not evidence
of a new incident from this sample. Swap is already almost exhausted; it is
not counted as additional usable space. Samples are not simultaneous at nanosecond
precision; natural exits can change admission after this snapshot.

A 10GiB pause threshold is not compatible with the unchanged supervisor contract.
SIGSTOP retains RSS and cannot free the current allocation; it only stops future
allocation while stopped. runtime_policy_wall90_v1.py:13-15,95,144-149,163-164
requires sample gaps <=30s, producer age <=30s and semantic retirement <=600s.
Stopping only the simulator makes its producer stale. sweep_native_cap1m.py:225,
228,237 applies TERM/KILL on guard failure/final cleanup. Stopping its supervisor
also yields a forbidden sample gap on resume. There is no registered checkpoint,
serialized simulator-state restore, memory-release-and-resume or transparent
cross-host migration path in the inspected execution contract. A frozen process
moved to slow storage would still need its live RSS unless such a separately
validated mechanism were implemented. This check neither signals models nor
changes that contract. Natural completion remains the currently safe release path.

Evidence: SNAPSHOT.json contains exact own/peer rows, PID generations, current
RSS/VmHWM, cgroup/PSI/events, pending canonical/current full-max costs, both budget
projections and source pins. SUMMARY.json carries the arithmetic and source paths.
No forecast/spec/budget/negative-result reservation was modified.
