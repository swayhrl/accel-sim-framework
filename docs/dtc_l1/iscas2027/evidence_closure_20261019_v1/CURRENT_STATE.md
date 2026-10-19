# Coordination state at publication

Date: 2026-10-19. Status: PLAN_PUBLISHED_AWAITING_NEW_COORDINATOR_ACK.

|Role|State at publication|Meaning|
|---|---|---|
|Existing AG4|USER_REPORTED_DISPATCHED; last published snapshot9ece18f6 is prelaunch registration|Not restarted; live launch count unknown; terminal results not assumed|
|COV1|GOAL_PUBLISHED_NOT_STARTED|No worker ACK/CPU/run result|
|SEM1|GOAL_PUBLISHED_NOT_STARTED|No worker ACK/CPU/run result|
|ROB1|GOAL_PUBLISHED_NOT_STARTED|No worker ACK/CPU/run result|
|New execution coordinator|GOAL_PUBLISHED_NOT_STARTED|No execution lock or simulator start|
|Paper|EN-v0.17 retained|No new performance merged|
|DC|User-owned|No assistant EDA execution|

This file is a planning snapshot. Live results belong to each worker's immutable published report. Do not mark RUNNING because a branch/Goal exists. The execution coordinator keeps its own updated CURRENT_STATE with exact worker/AG4 final commits; the planning branch must not become another dispatcher.

Read MASTER_PLAN for independent task gates, the32-start global cap and scientific STOP versus ordinary engineering recovery. All earlier completed/failed DTC cohorts retain their original records.
