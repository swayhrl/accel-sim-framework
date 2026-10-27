# Frame-read fail-closed engineering candidate V1

This independent package does not change frozen E38 sources, scientific inputs,
resources, existing claims, completed results, or running models. Main alone may
apply it to the current private chooser instance.

The scheduler TID 1723771 in parent PID 1498278 was present in both initial
read-only samples (R, then S). A partial JSON error therefore does not establish
that the unique scheduler died. Frozen RuntimeFrames reads terminal
`analysis/<cohort>.RESULT.json` without catching JSONDecodeError. Both initial
and fresh post-choice frame calls in frozen AgingChooser are uncaught. A writer
creating a JSON file before finishing json.dump can expose this path. This is a
reader-race vulnerability, not proof that the particular native.scan incident
originated in E aging or that a model failed.

`FrameReadGuard(aging)` stores the existing chooser/provider without installing
anything. Its `wrapper` is an outer admission gate. Each provider call retries
JSONDecodeError, UnicodeDecodeError and OSError at most three times, with 20ms
and 50ms delay. This bounds retry count and added sleep (70ms), not filesystem
call latency. Persistent errors return no proposal. No None/empty/previous frame
is passed to AgingState. Identity assertions and contract KeyErrors propagate.

If the second fresh frame fails after advance, private AgingState and call count
are restored. The frame provider is restored in finally. Its successful read
caches may remain refreshed; they cannot create a strict accepted result from
invalid JSON. Existing decision journal entries written earlier in an aborted
pass cannot be physically rolled back; `last_issue` explicitly identifies the
aborted pass and no proposal was returned. This is operational decision history,
not scientific result history. Main should expose this diagnostic alongside its
scheduler checkpoint. `last_pass_status` distinguishes valid and unavailable
passes; `last_issue` clears after a fully valid pass. No actual claims, consumed
UUIDs, resource forecasts, or model state are rolled back.

Main integration must hold the existing owner/aging lock and preserve its restore
chain: construct `gate` from the active E aging object; save its current wrapper;
set the owner's choose_dispatch and aging.wrapper to gate.wrapper together, so
the frozen E restore identity assertion still holds. Restore both together to
the saved wrapper before removing this gate. Do not overwrite the underlying B
chooser or the existing post-padding RuntimeFrames facade. Do not install twice.
This package deliberately performs none of those actions automatically.

Six CPU scenarios import the exact frozen E38 classes, including real temporary
half-written RESULT files. They test successful recovery, persistent corruption,
file-disappearance race, post-advance second-frame failure, UTF8/I/O failures,
and preservation of scientific assertions/contract exceptions. They start no
models and send no signals. A healthy subsequent scheduler pass may proceed
through every original gate; a current unavailable pass starts nothing.
