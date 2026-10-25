# Initial4GiB admission with40slot target

The user's explicit amendment replaces input-size/doubled-RSS estimates with
an initial4GiB per-cell planning envelope that grows only with observed RSS.
Admission reserves max(0,min(hard,max(4GiB,RSS))-RSS), plus actual cgroup/host
headroom; runtime checks actual headroom. The16GiB hard AS/RSS limit remains:
historical161closed points include an accepted sgemm peak15.246GiB, and a live
3MM point already exceeds4GiB. A4GiB hard-kill policy would discard valid work.
The original simulator/Core/cache/config/telemetry/strict/source ledger remain.

The target is40, with8fresh admissions per5seconds and distinct assigned cores.
Three still-live V1 frontend closures compiled the original full16GiB future
reservation formula. They expose no safe hot-reload/monitor-adoption hook.
Until they naturally close, the exact old predicate remains to prevent their
MEMORY_HEADROOM termination. The additional8GiB fresh compatibility margin is
removed. Once all original V1 cells close, the compatibility predicate lifts
automatically; remaining loaded V2 guards then check actual headroom, and new
V3 points use4GiB admission. This does not claim40models already ran. Only the
R10 metadata parent retired; all11models/frontends survived,172spent identities
remain unchanged, and no model is retried or refunded. Original four reviewed
Cutcp cells retain R6 handoff. New adapter/entry/controller identities are
explicitly versioned, qualified and published before new scientific starts.
