Read-only audit and independent original-IO retention amendment V1

Production read-only observation: 2026-10-27, owner PID1498278/start977758783.
/proc/1498278/fd/3 -> /root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock, inode61758282, owner WRITE FLOCK.
/proc/1498278/fd/4 -> /root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock, inode61622661, owner WRITE FLOCK.

R20.main opens original owner and held as local buffered File objects. The current lifetime prejoin amendment retains addon thread/hook/state/proof, not these original File objects. Affinity amendment stores only numeric proof, not R20 main-frame IO objects. Padding wrapper captures addon scheduler frame, not original R20 main. Existing other injected globals might incidentally retain a frame; this source-only audit cannot guarantee their live root reachability without an in-owner inspection. The independent amendment explicitly retains the two validated originals and reports their exact object IDs.

Only Main may apply: load the pinned retain_original_lease_io.py module in the existing owner main-thread GIL pending callback and invoke apply_in_owner(). Do not execute it in an external process expecting application. No import-time side effect. Main is sole applicant; Agent B has not attached/applied it.

Strong references live in __main__.DTC_L2_MLP_ORIGINAL_LEASE_IO_RETENTION_V1['objects']. It keeps the original IO objects through original main return and the existing prejoin lifetime hook. This does not acquire another lease, reopen a closed fd, modify lock ownership or change budget/registered science identity. It does not guarantee locks survive interpreter exit; the process must naturally outlive addon as already protected by lifetime_v1.

Discovery: exact R20 main frame locals owner/held if still present. Otherwise GC fallback requires exactly one still-live BufferedIOBase per original target fd/name. Already closed or absent original object rejects; no recovery by fdopen/open/dup/flock is permitted. Main-thread callback validates original process generation/source SHA and current fd target/inode/WRITE FLOCK before retaining. Correct repeated application is idempotent, exact object identities required.

CPU qualification: 9 PASS including actual isolated subprocess controls where original main function returns while a thread stays alive: without retention both original fds close; with retention both stay alive. Also wrong PID/start/target/fd/closed rejection, GC discovery of original wrapper, idempotence and monkeypatched flock prohibition. No production application, model starts, model signals, new lease acquisition or frozen-source mutation.
