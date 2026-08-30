# Dirty-Victim / TVD Premise Audit

Observed production order: victim selection → WAD reservation → native
writeback creation (`WRITE_BACK_REQUEST_SENT`) → static payload reassignment
(generation change) → writeback lower issue → `set_done` → WAD release.

M0b binds WAD observation only after the native writeback event exists.  The
source independently tracks WAD through `set_done`; the tag may already be
reused while that WAD remains outstanding.  For every ON-smoke dirty victim
with a valid prior handle, the old handle was non-live after static slot
reassignment (see `PRELIMINARY_METRICS.csv`).

Narrow preliminary label:

`CURRENT_MODEL_DOES_NOT_RETAIN_OLD_RESIDENT_PAYLOAD_HANDLE_TO_SET_DONE`

This does not yet decide TVD priority: OFF neutrality and representative WAD
workloads remain pending.
