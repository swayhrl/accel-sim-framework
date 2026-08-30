# Validation summary

All local integration self-gates pass. The source retains M1's single 1,152-slot namespace, static tag `i` to payload `i`, `payload_id % 4` bank mapping, sidecar/handle/owner/generation checks, and absence of production bypass traffic. M0a is default-OFF and observation-only.

Results remain `SPECULATIVE_PENDING_GATE` on `M0A_FINAL_PASS` and `M1_FINAL_PASS`. The original M0a live scan was not stopped, restarted, moved, rebuilt, or reused; an accidentally launched integration scan copy was immediately terminated before producing a status, and the runner was changed to compact-only by default.
