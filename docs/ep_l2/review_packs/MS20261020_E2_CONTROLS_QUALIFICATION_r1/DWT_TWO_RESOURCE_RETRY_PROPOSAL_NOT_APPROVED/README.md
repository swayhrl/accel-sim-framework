# Two missing DWT contrasts — proposal only, not approved

Replace exactly two **unstarted** original FWT LOCAL_DIAGNOSTIC cells:

| Old cell | Proposed DWT recovery | Prior charged invalid attempt |
|---|---|---|
| V2_FWT_7_21_S_L2_DATA_FREE | S_COPY_FREE | E027_a4c2f04e RESOURCE_LIMIT,exit-15/wait15 |
| V2_FWT_7_21_F_L2_DATA_FREE | W_ONLY | E028_f9b6ca83 RESOURCE_LIMIT,exit-15/wait15 |

Both new cells use the LOCAL_DIAGNOSTIC study/budget pool. W_ONLY keeps its physical P1 runtime and nonideal labels; this is an explicit allocation change, not a way to claim a new W_ONLY reservation or contingency allowance. The original32+8 and all group reservation totals stay unchanged. Exact current runtime/source/input/profile qualifications are reused; no native tests or production builds are repeated.

Two additional real starts:30→32/40,remaining10→8. The two failed starts are not refunded; contingency remains8/8 consumed. Expected200–260MB,hard maximum0.75GiB; sequential estimated30–70min, each original10800s timeout retained. Original6/20GiB generation and time/resource guards remain. Fresh capacity must cover both full384MiB bounds. Default one at a time after the observed RAM volatility.

Value: complete two predeclared missing DWT comparisons using its current full S/F anchors. W_ONLY versus F identifies only joint V+RO/state effects; COPY_FREE exempts copy services **and fixed copy-staging retry delay** and remains diagnostic. Unstarted FWT data-free points lack accepted FWT anchors. No favorable endpoint is rerun, no new workload selected by speedup.

This is a new exact two-slot scientific allocation and retry authorization request. Original user instructions require approval for new slots; the earlier four-cell approval did not authorize retries. No matrix,registry,budget or controller has been changed by this proposal; no run is launched. Apply only after explicit approval and all original gates. Main61 and all old results/HOLD remain.

Scientific cost: two distinct planned FWT configurations are forgone to fund retries of two existing DWT configurations. The32 retained matrix rows are bookkeeping, not a claim of32 distinct runtime configurations after this revision. Both original DWT failures remain separately visible and charged. This loss of two unique planned configurations is part of the explicit approval request.
