# Current completion and memory admission review

Frozen at 2026-10-28T04:30:18.196375+08:00. Primary scope remains 350 cells / 35 frozen complete inputs, 344 fresh grants and six exact P0 references. 262 new strict/archive/native-restore PASS plus six references; 24 models actually live; 57 unstarted. One spent original scan/M16 engineering failure remains unaccepted, cycles=null, with its own independent negative archive. Counts are time-stamped snapshots, not a new inference population. The raw 350-result snapshot gives each exact cohort and result SHA. No supplemental grant or launch has occurred at this checkpoint.

## Why not all pending points start

The owner is alive and its loop checkpoint fresh. The existing aging policy protects released admission capacity for the oldest large lavaMD DH-P0 (full predicted peak 81.178 GiB). Other short jobs can currently fit physical RAM but the protected-capacity priority restricts their admission. This scheduling restriction is separate from physical memory exhaustion and is disclosed here.

Measured host MemAvailable 129.87 GiB, cgroup effective headroom 155.72 GiB, observed live-model RSS 76.50 GiB. The existing admission policy yields 107.26 GiB future-growth budget, already committed 32.37 GiB, leaving 74.89 GiB for new full forecasts. The retained failed-generation reservation is 1.392 GiB; it has not been released through a fake completion receipt. At the independent latest aging observation protected=73.95 GiB and slack=74.84 GiB. Snapshots are not atomic with each other.

The current memory floor/fraction is not claimed optimal. Free RAM is partly forecast protection, and partly conservatism; a more aggressive future-only policy is under review. No new 10-GiB policy or process-pause mechanism is represented as installed. SIGSTOP alone retains RSS and cannot recover memory; old unchanged heartbeat supervision can classify a stopped model as stale and terminate it. Therefore an emergency 'pause some models at 10 GiB' is not a functioning memory-reclamation solution. Admission suspension, fresh growth forecasts, cgroup/host pressure monitoring and letting short jobs complete remain the current safe mechanisms. Changing those operational limits requires a separately qualified immutable overlay, without overwriting the old policy or evidence pins.

## Completed operational change and candidate

Actual transport-verifier V3 was bound at 04:19 CST in the same owner, journal and factory. Its ACK, real shadow and fresh transport proof are included. Original verifier08ae still honestly HOLDs; the distinct9a verifier permits only inode variation on eight exact added SSHFS context entries while preserving original seals and all other checks. This changes no input, model configuration, budget or accepted result.

The same-input/design P0 dependency preference is a candidate only: 36 CPU tests PASS, source a650a4c2..., not installed or registered. It can only replace a variant with its eligible same-input/design P0 after re-running the full existing admission chain; it cannot bypass the aged large-job reserve. A separate one-shot short-P0 priority integration is still being qualified and is not claimed active.

## Scientific evidence and review questions

The prior science checkpoint at commit f5192e76e902845d6f5ef0cb42e4fe55ec0002df contains raw-closed 257 accepted results, 189 DH/P0 pairs, common-21 factor GM and counter evidence. This newer operational snapshot does not recompute or promote a uniform winner. No non-P0 CH matching result is available, so DTC relative advantage from new L2 parameters is not yet established. Source/binary/clock/input/scientific contracts and English v0.23 remain fixed.

Review: (1) distinguish physical memory limits from the large-job protected-priority rule; (2) assess a more aggressive future-only admission margin while retaining real growth and cgroup pressure checks; (3) preserve raw failure versus independently labelled supplemental-trial identity; (4) reject partial-population GM as a whole35 configuration winner. Goal remains active; no scientific completion or new phase is declared.
