# Guarded admission V1 — Agent A candidate

**66 CPU component checks pass; zero actual model starts. Production remains on HOLD because the current native supervisor rejects an intentionally paused producer after30 seconds. Nothing is installed, registered, dispatched, signaled, or changed in production by Agent A.**

`PAUSE_SUPERVISOR_COMPATIBILITY_BLOCKER.json` records the exact source SHA and lines: the telemetry receiver fails after30 seconds without producer output; the current native worker then terminates the model. Pausing the worker too violates its resource-sampling cadence on resume. Empty-resolver integration and synthetic launcher tests do not establish real long-pause compatibility. A concrete pause-aware observation contract and eligible supervisor identity are required before production use; existing healthy workers cannot silently acquire that identity.

The production frozen engine, resources, frontend, strict validator, execution plan, Core/Framework, binary, all270 scientific options, input identity, canonical forecast, RSS/AS limits and original execution binding are unchanged. Six frozen source/control files were hashed before/after the isolated tests.

## Admission policy

The existing resource result remains intact as `base_resource_receipt`. Its complete future-peak total is explicitly **not** represented as the effective admission gate after the overlay. The actual decision and its provider SHA are separate fields.

- The new candidate retains its **full canonical forecast**. Lava remains 87,164,072,756 bytes (about81.18GiB), not a reduced startup estimate. RSS/AS caps stay unchanged.
- Foreign reservations, claim/candidate reservations, unresolved generations and unidentified live generations remain fully reserved.
- Only another already observed live generation of this request can replace its remaining-future-peak reservation with a fresh growth envelope: maximum of256MiB, 10% observed RSS, and twice the positive measured growth extrapolated30 seconds. Already observed RSS increase since the guard sample is also covered. The original reservation is never increased by this discounting calculation.
- Headroom uses the lower of the original resource sample and the fresh guard sample; cgroup raw headroom additionally bounds admission. Both host and cgroup retain10GiB floors. Existing pressure reasons and all disk/inode/write-ceiling checks stay active.
- If the full candidate still does not fit, the result is **HOLD**. There is no automatic forecast reduction or automatic fallback selection.

The CPU synthetic test demonstrates a case where the original all-future-peaks gate holds but the guarded gate fits the complete Lava forecast. It does not assert that current production headroom fits Lava.

## One explicitly selected pilot

The eligible pilot identities are existing legal unused DH-P0 points for Lava, SGEMM or scalarProd. The frontend never chooses among them. At any instant the registered `active_resource_admission_token` selects exactly one cohort.

The token binds request, exact cohort, nonce, epoch2, boot ID, owner PID/start, canonical specification SHA and dispatch-binding SHA. Lifetime is at most120 seconds. Immutable token history is retained for terminal verification; no consumed identity is reset or refunded. Rotation, expiry, wrong epoch/owner/cohort/spec/dispatch or an unselected fallback holds admission.

`REGISTRY_METADATA_TEMPLATE_NOT_AUTHORIZATION.json` describes the required fields. Its placeholders and example status are not authorization and must never be registered.

## Real guard required

Use Agent B's frozen `memory_guard.py`, SHA256 `d65ca467f0fd9570cc265a43ee7776159a3c3014dea6c9e7660123ea7b11b016`. The28-key `POLICY.json` is the complete canonical union of B's defaults and A's admission policy. Its raw-file SHA equals B's merged-policy canonical SHA: `a1f62ec55947a1ce9f913bf9af1fadb16020afe748ef31148eb504aa45a4a3a4`.

Admission requires all of the following:

- Fresh heartbeat within2 seconds, completed guard warmup, exact epoch/boot/request/overlay/policy/source and active pilot-token SHA.
- `signals_enabled=True`, `shadow_mode=False`, `aggressive_admission_armed=True`, `healthy=True`, `fault=None`, `fresh_admission_allowed=True`. Missing or false aggressive-armed flags hold admission. B's fault path freezes its strongly identified cached owned handles when armed; this still does not resolve the frozen supervisor's pause/freshness conflict.
- Owner/monitor PID and start exactly match the registered existing parent lease. The separate guard native TID and start must exist under that parent's `/proc/.../task`, remain in a healthy state, and match the registered guard token. A dead thread holds even when its last heartbeat is still young.
- Pause-journal prefix hash and canonical paused-handle-state hash are verified. A stable guard identity is frozen into the additional binding; changing heartbeat samples do not change that binding.

B's20GiB soft pause,10GiB hard floor,30GiB resume hysteresis and reaction margins remain present. SIGSTOP retains RSS; the scheme cannot promise protection against unbounded allocation bursts or an indefinitely blocked OS. A fault stops new admission. The original runtime resource sampler retains its existing behavior and caps; this overlay does not rewrite it to kill healthy models on low headroom.

The older `guard_monitor.py` in this directory is diagnostic-only and **not an eligible production guard**. It cannot satisfy the required signal-enabled parent-thread heartbeat. The metadata template pins B's source instead.

## Execution and independent acceptance

`guarded_frontend.py` delegates all ordinary operations, including archive, unchanged to the original frontend. Only explicit `--guarded-admission-v1` experiment prepare/inspect/run-native invokes a freshly loaded private instance of the frozen engine. No frozen file is edited.

The original `e.binding()` remains byte-for-byte the same object value. The additional top-level `resource_overlay_binding` records the base provider, new provider, policy, B guard, additional strict gate, CPU qualification, publication receipt, stable guard identity and unique token. It never impersonates the original binding.

The actual observer adapter executes the transformed native function in `native.__dict__`, not a copied namespace. CPU tests checked that the compiled function resolves the final exclusive chain and **actually writes matching original and additional bindings into INTENT, LAUNCH and PID files**. The LAUNCH/PID test uses an explicitly synthetic CPU launcher, maps and BA telemetry inside its own fixture; it is not a scientific model or accepted performance result.

The coordinator must integrate `additional_strict.py` **after** the unchanged original strict validator and **before** a guarded result is accepted/archived. It verifies all three extra bindings, the untouched original binding, approval/publication/source/policy/token history, full candidate reservation, heartbeat snapshot/hash/flags, guard identity, pause-journal historical prefixes and target-generation pause/resume identities. An owner-selected cohort cannot omit its extra binding to fall back silently to ordinary acceptance.

Reservation arithmetic is independently closed: changed/unchanged rows must correspond one-to-one to archived base rows, original values must match, nonlive and foreign reservations cannot shrink, the total must equal base total plus every per-row delta, and the ceiling is recomputed from archived base/guard samples and fixed floors. Changed-generation UUIDs use authenticated archived guard evidence and the request's immutable consumed UUID; terminal validation does not require a historical process to remain alive.

The guard additionally requires a source publication receipt with `READBACK_VERIFIED`, a concrete40-character commit and exact component source SHA readbacks before native execution. CPU fixture approvals/publication stubs are explicitly rejected against the production root.

## Qualification

`CPU_QUALIFICATION.json`: SHA256 `48d629d4c273a2edc4db2d9ea3f1a377c466bda79816961a16d99161b116fad5`.

66 checks cover old-request refusal, wrong/expired/unselected tokens, source-publication gating, fixture replay refusal, fresh/stale/shadow/signals-disabled/dead-thread/pressure/journal/token/unarmed heartbeat cases, original/guarded resource accounting, full candidate preservation, actual original native prepare, exact launcher prefix at intercepted Popen, actual compiled INTENT/LAUNCH/PID writes, all270 scientific options and limits, independent extra-gate and reservation-math tamper tests, original strict natural-completion compatibility and unchanged ordinary frontend delegation.

The exact B guard was also instantiated in an isolated CPU process with B's existing explicitly permitted CPU fixture root and an **empty resolver**. Its genuine signal-enabled dedicated-thread heartbeat fed A's actual native prepare successfully. It acquired zero simulator handles and sent zero signals. This establishes schema/source/policy interoperability; production-parent insertion and pressure soak remain coordinator integration work.

The original strict compatibility test read the real already accepted gaussian DH-E384 result twice, once with only virtual additive top fields. The full terminal result remained identical. No result files were modified.

## Frozen implementation

- `guarded_native.py`: `19c12c937b4d034b5411f5ca8a54ffb2b5bd0681b2a3ac121d2f9fd5d912040c`.
- `additional_strict.py`: `0c6c7a392c0dbc7a2ce46eaa96b87cef27735923583cb63bdba97cde25905c49`.
- Base engine SHA: `e8276aadbb243b29166d89e5e937de260e6017061b475b62ac9c6c6f3dc3825a`.
- Original complete binding canonical SHA: `0e16e30d88a6c7c6266b7044b5645c24cf98f869a058a30a5f1fd29d19bf392a`.

Local and164 paths share the suffix `agents/A/guarded_admission_v1/`. The CPU test fixtures are separately retained under `/root/data/dtc_l2_guard_CPU_A_*`; they are never production registrations, model attempts or accepted results.
