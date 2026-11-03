# Actual first16 admission diagnosis

Confirmed engineering admission livelock: current source-pinned stage2_ops chooses CPU/RAM-fit candidates, saves each claim and submits workers, but does not check aggregate disk budget before each claim. A burst of remaining claims can make all prepare/run checks HOLD before a model starts. Some PREPARE commands pass and their corresponding run-native recheck holds after later claims inflate the shared reservation. Unconsumed identity retry is legitimate; no old UUID is restarted.

All16 fixed CPU bindings are distinct and within owner main-thread32–63. Four consumed models have exact live PID generations and valid CPU bindings. RAM is ample. The full16 projection, preserved peer reserves and exact free-space deficit are in DIAGNOSIS.json with timestamp and source SHA; new EP reservations increased the needed native envelope, so prior12.435GiB threshold is no longer current.

Coordinator chose the minimal forward fix: a CPU-qualified, source-bound, same-owner private choose_dispatch wrapper checks resources(real canonical spec,True) before adding each claim. Disk/RAM insufficiency returnsNone without adding a claim or consuming identity. Existing models continue. New claims resume as natural completion/archive frees reserved future writes. Preserve5GiB safety, foreign budgets, all original sourcepins/specs/registry/strict/input/config/binary and controller identity. Agent A only diagnosed; it performed no mutation or model operation.

A simpler tactical alternative is safe migration of self-owned nonlive assets to164 to release current deficit plus margin. It is not necessary to change scientific parameters or reduce safety floors. The chosen wrapper handles later foreign-budget growth without recurring batch livelock.
