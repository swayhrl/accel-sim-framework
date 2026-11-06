# Independent CPU evidence for same-owner recovery

Status: CPU fixtures PASS; **no actual owner installation, registered runtime edit, simulator/GPU run, scientific registration, UUID consumption or dispatcher operation was performed**. Native temporary locks and fake identities are plainly CPU-only and removed after checked-path cleanup.

## Actual OFD and executor unwind behavior

The27-check fixture reproduces a typed RESOURCE_HOLD raised inside three nested real ThreadPoolExecutor contexts. Archive/review executors drain and stop. The old scheduler frame remains suspended exclusively in model executor __exit__/shutdown/join while an actual healthy CPU future waits on an Event. A new open-file-description is not substituted: os.dup duplicates the original held FD. Independent subprocess attempts at LOCK_EX|LOCK_NB fail before capture, after duplicate capture and after the old context later closes its original file. Closing one duplicate still preserves exclusion; only closing the final duplicate lets the independent process acquire the lock.

The fixture also demonstrates a prohibited counterexample: explicit LOCK_UN through any same-OFD descriptor releases the flock even while duplicates remain open. Production handoff must preserve the frozen close-only old cleanup and never issue LOCK_UN/reset/reopen to imitate continuity.

The original executor cannot submit after shutdown, the original old body never resumes admission, the original started marker is not reset, a duplicate handoff generation is rejected, and an adopted spent fake UUID/PID retains exactly its original future without another worker invocation. A separate isolated state-machine test serializes short admission while four healthy CPU jobs run concurrently; typed HOLD defers an unused identity and unexpected failure permanently pauses new admission while healthy jobs finish. These generation/adoption-policy tests are **isolated invariants**, not a substitute for review of the actual recovery controller.

## Actual R implementation helper tests

The12-check supplement directly imports the tested R module and calls inspect_unwinding_scheduler, capture_handoff, resource_hold, PlainPool and PlainFuture. An isolated source-compatible run_scheduler frame uses the actual required variable names and a real native temporary lock inode. The actual helper captures the existing original future and os.dup lock reference, including non-inheritable duplicate behavior; it never calls install. The generation marker is published by the CPU fixture under the same documented caller precondition; capture_handoff alone is not falsely claimed to publish that marker.

Actual PlainPool tests cover bounded queue PoolBusy/HOLD, no silently enqueued rejected work, correct results, typed task HOLD transport, unexpected exception preservation, pool usability after task exceptions and sentinel shutdown of every private worker. The full R implementation snapshot tested is R_RECOVERY_SOURCE_TESTED.py; both supplements assert the loaded source SHA stays unchanged throughout the test.

## Real interpreter-return boundary

The child script genuinely ends its Main body. CPython then enters the original lifetime hook and waits for the old keeper, the keeper naturally finishes, the hook returns, and concurrent.futures._shutdown naturally becomes true. Only then does a non-daemon recovery master create and submit to the **actual R PlainPool**. Results and a CPU-only /usr/bin/true subprocess complete; sentinels stop the private workers; the interpreter exits naturally with return code0. At the same point a normal ThreadPoolExecutor submit is rejected for interpreter shutdown. No code assigns/resets the futures flag, no toy same-name pool is substituted and the R module adds no atexit hook. The JSON records the actual ordering.

## Required actual-install checks and risks

These fixtures do not prove the actual owner is presently at the same valid frame or that its real FD3/FD4 lease, identities, pending callback, source pins and live PID/maps are valid. Main/R/D must independently confirm those real conditions and obtain their ordinary explicit forward engineering release. A missing/changed old frame, active old archive/review worker, wrong inode, incomplete existing identity or source mismatch must fail closed. Never adopt an uncertain identity by launching it again.

The old-generation dispatcher must remain unable to re-admit; new operational generation uses the same legal owner, continuous lock OFD and immutable science request/UUIDs. Already spent model futures may only be observed/adopted. New admissions must use unused registered identities and verified PID/start/maps binding to end their short serialized startup phase; this must not serialize entire model lifetimes.

Unexpected failures must not cause another executor-context unwind. Persistent failed-future entries must be explicitly retained/quarantined without repeatedly starving other closure processing. R reports its current source has per-future harvest/quarantine, orphan cleanup guarded by consumed/INTENT/real closure and dirty reservation resynchronization; this packet's helper tests do not certify every full recovery-loop branch. D's independent transform and end-to-end CPU review remains required.

Plain non-daemon workers and preserved modules working after the futures shutdown boundary do not themselves prove every real Main lifetime/callback condition. The same owner must remain alive, keep its science authority/lease and safely close the recovery pool at the authorized terminal boundary. No actual lifetime hook, private global shutdown flag, old request or production Core is reset by these tests.
