# Shared-route validation to sealed EP-entry execution

Status: **12 new CPU execution fixtures PASS; production NOT_ACTIVATED.**

The new guarded_sealed_invocation_candidate.py closes the specific validated-routing-to-executed-shell-bytes race in a CPU-only engineering path. It does not create scientific authority or a production dispatcher.

## Implemented primitive

prepare() validates the current shared Native against the pinned reviewed preimage and finite authorized foreign grant. It opens the exact scoped entry with no-follow bounded read, checks its immutable SHA, copies those verified bytes to a Linux memfd, and applies WRITE/GROW/SHRINK/SEAL seals. Prepared.fd is an open immutable execution artifact. The shared path is never executed. Later shared-file or scoped-path replacements cannot redirect the selected entry bytes.

The executed command uses /bin/sh /proc/self/fd/N with explicit argv array, exact supplied environment and inherited fd. This avoids command-string interpolation. The production integration must continue to qualify /bin/sh and the actual runtime environment through its existing runtime contract.

invoke_cpu_stub() deliberately accepts only the exact constant harmless shell/Python JSON-print stub. It rejects all nonstub entries, including real scientific Native. No simulator, foreign handler, old runtime or actual production scoped entry was invoked in these tests.

## Actually executed checks

12 methods passed:

1. Positive current exact reviewed foreign insertion followed by sealed stub execution.
2. Shared path replaced after validation by a malicious shell: approved sealed stub still executes.
3. Scoped entry changed before pin: rejected.
4. EP route changed before pin: rejected.
5. Scoped entry atomically replaced after pin: approved sealed bytes execute.
6. Scoped entry rewritten in place after pin: approved sealed bytes execute.
7. Memfd write and truncate attempts fail with EPERM; stub stays intact.
8. Space/newline/Unicode/metacharacter argv and environment preserved; command substitution is not evaluated.
9. Nonstub entry cannot be executed by the CPU fixture API.
10. Closed handle cannot execute.
11. Unapproved/replaced foreign handler grant rejected.
12. Scoped symlink pin rejected.

The earlier17 guard/resource/loader fixtures remain separate. Combined total29 methods.

## Main integration contract, not activation

After fresh family authorization and full qualification, Main can use the prepared fd in its one authorized consume/launch transaction. The concrete integration shape is:

    with Main_global_admission_lock:
        validate_fresh_authority_exact_spec_mode_input_and_resources()
        prepared = prepare(current_global, pinned_base, pinned_grant, pinned_scoped_entry)
        verify_actual_Source5_ELF_library_and_owned_runtime_dependencies()
        bind_one_shot_intent_and_consume_once()
        launch_native_shell_from_fd(prepared.fd, exact_argv, exact_environment)
        close_parent_fd_after_child_inherits_it()

launch_native_shell_from_fd is an integration operation, deliberately not supplied as an unrestricted production executor by this CPU fixture module. The supplied tested stub launcher demonstrates the exact pass_fds and /proc/self/fd technique. The old global/native/runtime are not patched by this work.

## Boundaries that remain open

- **Closed at CPU engineering level:** shared-route/scoped-shell pathname replacement can no longer change the sealed shell bytes executed by the demonstrated handoff.
- **Not closed:** the sealed shell may reference owned Python/frontend/runtime/module/config paths. Those dependencies must remain pinned and immutable at use, or be independently sealed/snapshotted by Main. A sealed shell alone does not prove a sealed Python dependency graph.
- Actual ELF/library SHA and source repository identity remain the existing engine's streaming verification responsibility; small-artifact16MiB reads are not applied to large libraries or Trace.
- Full new family mode/runtime/native/source qualification, live foreign resource mapping, CPU affinity selection, scientific authorization, consume and application acceptance are not granted by these tests.
- Environment/argv transport was proven with the harmless supplied contract; this does not upgrade scientific environment or mode NI.
- A later unreviewed shared-route change will be rejected on the next prepare. Already prepared execution cannot jump into it because that path is never executed.

Therefore production remains **NOT_ACTIVATED / HOLD integration**, while the concrete global routing-to-entry TOCTOU mechanism now has executable positive and negative proof rather than only a design note.
