# COV1 source-only review of three real external CPU roles

Status: PROPOSED_NOT_EXECUTED_NOT_AUTHORITY_QUALIFICATION. Current source anchor is
coordinator `7e7bd82423f0f5807e2d89bb7fe779d21be13148`, with baseline69f22e88. Only immutable Git source
and registration were read. No CPU test, compile, ptrace, /proc/resource sample,
process polling, simulator, new lock or background observer was run for this
review. Parent is separately integrating canonical AG5 generations; this review
does not re-audit AG5/BASE or repeat the existing12 synthetic-row negatives.

Deliverables:

- `SOURCE_REVIEW.md`: specific source gaps and the minimum interfaces needed.
- `REAL_ROLE_QUALIFICATION_PLAN.md`: one bounded actual-work observation cohort,
  including short-role handling and the observer's own role.
- `QUALIFICATION_CASES.tsv`: actual observations and exact acceptance scope.
- `READ_ONLY_BINDING_CONTRACT.json`: proposed data/interface contract. It is a
  design example, not executable registration, release, completed observation,
  or authority to start any role.
- `SOURCE_BINDINGS.tsv`: exact reviewed Git blobs. The existing parent role
  contracts already bind the COV/SEM/ROB source hashes and argv variants.

Source findings target the69f22e88 caller, not the later in-progress parent
copy. Parent has acknowledged and is preparing fresh stat/status around current
cmdline/cwd/exe plus explicit process_reader injection, and AG5 tracer/Tgid/
retired checks. Those changes are pending independent immutable source and
runtime receipts; this pack records requirements, not a PASS for unseen code.

Historical source-only/tiny-reference evidence in the surrounding COV1 pack
keeps its prior scope. The latest parent report says disk was restored, but
host IO was still above25. This review does not make a current resource claim
or run another preflight. New observation remains blocked until the unchanged
paired host+cgroup CPU admission passes and exact source/role publication is
read back. No simulation budget or application denominator is changed.

Current update: read parent7e7bd82423f0f5807e2d89bb7fe779d21be13148 and its
V2 qualifier/registration after the initial69f22e88 review. Fresh current
attributes, peer tracer/Tgid/retired checks and post-root descendant ownership
publication are now source-fixed. The plan consumes those fixes and requests
only the remaining actual-role/release/admission/launch/observer/resource
interfaces. V2 remains unreleased pending new ELF/manifests; no new runtime
qualification is claimed. See SOURCE_REVIEW's current-update section.
