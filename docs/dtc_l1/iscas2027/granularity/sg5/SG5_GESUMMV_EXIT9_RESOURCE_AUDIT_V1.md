# SG5 GESUMMV exit -9 resource audit (V1)

The immutable SG5.C2 GESUMMV observer-ON IO and OO attempts are preserved
FAIL evidence. Both terminated with status `-9`, empty stderr, and incomplete
observer/cycle/instruction reports; neither is a simulator result.

The shared local audit in
`../sg3/SG3_GESUMMV_EXIT9_RESOURCE_AUDIT_V1.md` found cumulative cgroup
resource-pressure evidence (`memory.events: oom_kill=16`) but no readable
per-PID kernel record. Consequently this document does not assign a cause to
the status `-9`. The only authorized treatment is a fresh-UUID retry, with
heavy GESUMMV processes capped at two across SG1/SG3/SG5 and strict validation
immediately upon terminal state.
