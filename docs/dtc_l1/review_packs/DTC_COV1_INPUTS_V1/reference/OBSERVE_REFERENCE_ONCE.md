# One actual COV entry with bounded observation ACK

Status: **SOURCE_PREPARED_NOT_EXECUTED / NOT_RELEASED**. No import, AST/syntax
compile, test, process/pipe launch, resource sample or actual observer callback
was performed. The two existing mathematical source files are unchanged.
`OBSERVE_REFERENCE_ONCE_CONTRACT.json` proposes the new exact argv/environment;
it includes this exact wrapper's digest but grants no permission. The complete
manager/import/parent closure and release remain separately frozen by parent.

The new `observe_reference_once.py` launches no child. When called as the exact
`python3.10 -E -B` script in the COV worktree, it validates the exact five-key
existing clean environment plus the one decimal
`DTC_COV1_REFERENCE_ACK_FD`. The explicit inherited fd must be a pipe at fd>=3.
It sets that fd nonblocking, verifies the unchanged two source hashes, then
waits once through select with a monotonic deadline at most5s. EOF, a wrong
byte, extra immediately available bytes, interrupted/error/expired wait all
fail before any test. Only the single byte hex41 (`A`) is accepted. The fd is
closed in finally and the fd environment key removed before tests. Source
hashes are checked again after ACK. There is no sleep or second observation.

On ACK it sets the unittest argv to the original script with `-v`, then calls
`runpy.run_path(original_script, run_name='__main__')` once in this **same
Python process**. The wrapper sits beside the original script so `-E -B`
retains the fixed source directory for its existing local import. No math
case, fixture or implementation is copied/changed. PID/start_ticks remain the
same across the bounded wait and the actual four-test invocation; normal
unittest exit code/output are retained. This is a real finite controller with
an observation rendezvous, not an additional test run or a simulator canary.

Parent's separately reviewed manager integration should:

1. Freeze the new argv, wrapper hash, two unchanged source hashes, interpreter,
   manager/source/import/role/policy/release closure,60s role deadline and1MiB
   output limit. Existing direct-tiny argv does not qualify this new entry.
2. Keep the existing full fresh R2/authority gate. For the COV phase only,
   create its own anonymous pipe, pass only its read fd with `pass_fds`, and
   include that fd in the one explicit environment key. Close the manager's
   read copy after its successful direct Popen; publish only actual launch
   data, never pipe/pidfd/Popen handles.
3. Immediately run the actual source-bound review and the parent's required
   binding-negative check against this same actual waiting PID/ticks/current
   attributes. Emit their exact receipts. Only after successful qualification
   write the single ACK byte and close the manager's private write fd.
4. On rejection, timeout or any exception close the write fd so the child
   observes EOF. Preserve the existing own-handle/pidfd-only cleanup and
   terminal receipts. Never hold or retry beyond5s, re-run completed four
   tests, discover a replacement PID or claim a live sample that missed it.

Parent must retain ordinary60s runtime/output limits; this source bounds only
the rendezvous, not all Python/kernel execution. A callback taking too long
will produce an honest incomplete observation and no math execution. A
successful observation concerns this one actual COV controller; it establishes
neither joint three-role overlap nor continuous/global simulation authority.
