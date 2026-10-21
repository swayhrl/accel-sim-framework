# Completed-native decoder-only recovery candidate

`recover_completed_parser_only.py` is a candidate; preparation ran only AST/pure equivalence controls. It has not parsed an application, registered a Q, resolved a HOLD, written the registry or launched any native/simulator/compiler. Root E reviews/publishes the new decoder/Q/owner evidence and seals the intake before explicit execution.

The script reads only `parser_recovery_r1/PARSER_RECOVERY_INTAKE.json` and requires `--execute-sealed-intake --intake-sha256 <exactsha>`. Intake schema:

```json
{
  "schema": "E2_COMPLETED_NATIVE_PARSER_ONLY_RECOVERY_INTAKE_V1",
  "approved_by": "E",
  "new_application_starts": 0,
  "owner_review": {"path": "<real review JSON>", "sha256": "<real SHA>"},
  "attempts": [{
    "attempt_id": "E037_a423c80f",
    "original_receipt": {"path": "<original FAILED run_status.json>", "sha256": "<original SHA>"},
    "new_qualification": {"path": "<separate parser-revised Q>", "sha256": "<new Q SHA>"},
    "recovery_subdirectory": "parser_recovery_r1"
  }]
}
```

The owner review must say `reviewed_by=E`, `status=PARSER_ONLY_ORDERING_FIX_VERIFIED`, `scientific_semantics_unchanged=true`, and contain `evidence` references with real paths/SHA values. Bind the source-order repair review, exact new decoder/seal and bounded engineering checks; this is not a mechanism/native qualification change. The input agent's new parser is `parser_recovery_r1/parse_capacity_terminal.py`, SHA `63cce0b814827a61b270b522b012f2620e55139dc24d61cbd29d74e48d69fb77` at delivery. E root must freeze actual current bytes rather than trust this prose.

Root constructs each new Q as a separate file. Only top `terminal_parser`, `parser_seal`, `qualified_unix`, `scope_note`, optional `parser_only_revision`, plus nested `capacity_diagnostic.parser_seal` may differ. Top/nested new seals must agree. All source/binary/archive/build/native/gates/semantics/input/scopes/supported-profile data remain exactly equal. The script registers through original Coordinator; original Q and its SHA are never overwritten. It creates a new spec from the executed original, changing only Q/parser/input audit. Independent inspect rehashes all relevant source/runtime/config/trace assets. The audit must be exactly equal except the explicit new qualification SHA and new parser reference; parser change is recorded, not hidden by the “same audit” assertion.

Execution starts only after the original controller naturally STOPPED, its exact process exited, original lock is free and active/uncertain E apps and campaign leases are absent. Only the Python decoder executes under original1CPU/8GiB test lease,64MiB new metadata budget and unchanged physical guards. There is no application reservation/start/finish call, second controller, build or simulator invocation. An unresolved parser-process constructor/exit keeps the original test lease for explicit owner reconciliation.

Each endpoint must retain actual original native exit/wait0, normal/released state, exact PID/start_ticks/boot/guardian/startup/exit binding, original raw SHA, native executable/config/aux snapshot hashes, complete instructions/kernels and full64slice data/ownership/resource/WB/drain validation. New parser CLI and original scoped terminal validator must both pass; exit0 alone is insufficient.

Results go into a new child of the original attempt. Original application NATIVE_EXIT/READY are copied byte-for-byte; root `raw.log` is a symlink reference to the immutable original raw. New `input_spec.json`, audit, terminal summary and recovered `run_status.json` satisfy existing accept_pair/report read paths. The application native binding still truthfully names its originally executed Q; the receipt explicitly explains the decoder-only Q revision. Parser's own durable process evidence stays under `parser_validation/` and cannot replace application exit evidence.

Under original `coord.locked`, `accepted_results[original_attempt_id]` receives the new recovery receipt only after full validation. Original attempt state remains FAILED, original receipt pointer/SHA and `data.runs` remain unchanged. `parser_recovery_history` preserves the exact original attempt/HOLD, new receipt/Q, intake identity and zero new starts. Preexisting accepted endpoints and original scientific history cannot change.

E037/E038 share the same original CFD Q. If both fail, current HOLD may name E038 while earlier E037 HOLD remains in hold history. The script therefore resolves **once per original Q, after every requested endpoint independently passes**, through existing `resolve_scientific_hold` with the exact current hold timestamp and SHA-bound cohort evidence. All failed bytes and hold history remain. New acceptance does not mark old parser/Q evidence successful. Do not separately call per-row `recover()` expecting cohort resolution; use the sealed main entry.

Partial recovery is intentionally retained; the script refuses to overwrite any recovery directory or accepted pointer. If a later requested decode fails, keep completed recovery evidence and old HOLD, review that engineering failure, and explicitly prepare the next bounded recovery revision; no simulator rerun or budget refund follows. Root updates subsequent queue/plan references to the revised Q/parser and publishes accurate accepted-result/recovery history before further applications. The original attempt's FAILED state is historical, while its accepted-results pointer is the independently recovered current endpoint; status reports must present both facts.
