# Execution coordination state

Updated: 2026-10-19 20:27 Asia/Shanghai. Plan anchor: `46df82670a56a4498b6d6e23ad57859eb7c36945`. Maintained only on `hrl/iscas2027-dtc-closure-exec-174-v1`; planning branch unchanged.

|Role|Actual state|Immutable evidence / branch|
|---|---|---|
|Existing AG4|Live runner/simulator and execution lock observed once; no terminal publication; untouched|`9ece18f6fdb6de16ee95f35caa6fad1fec765fc9` is preregistration only|
|Coordinator `/root`|STARTED_SAFE_PREPARATION_ONLY; sole designated later simulation coordinator, not admitted to dispatch|`execution/START_RECEIPT.json`|
|COV1 `/root/cov1`|ACK received; parallel preparation; tests NOT_STARTED|ACK `c328acaa38c84ab27a1b5fbe8a8e15e9a2fd26df`; `hrl/iscas2027-dtc-cov1-inputs-174-v1`|
|SEM1 `/root/sem1`|ACK received; parallel preparation; tests NOT_STARTED|ACK `5e6c13b733c08470061bb0f953389c1c2ebc8a90`; `hrl/iscas2027-dtc-sem1-values-174-v1`|
|ROB1 `/root/rob1`|ACK received; parallel preparation; tests NOT_STARTED|ACK `a8a0fc962ea65f612db5a442e27157cf228dd1ae`; `hrl/iscas2027-dtc-rob1-controls-174-v1`|
|New CPU tests / compiles / trace scans|NOT_STARTED; WAIT_AG4_TERMINAL_AUTHORITY|No CPU PASS claimed|
|New full simulations|0/32 actual starts, no executable family frozen, no execution lock|`execution/BUDGET_LEDGER.json`|
|Final F|NOT_FROZEN; no AE/AD result inferred|`execution/SELECTION.json`|
|Paper / DC|EN-v0.17 retained; DC user-owned|No paper modification or EDA execution|

Worker worktrees start at the pinned plan commit and have separate output roots below `/workspace/dtc-evidence-closure-20261019-v1/`. Workers cannot launch full simulators. Unexecuted code is PREPARED_NOT_TESTED. Authoritative deliveries will be exact GitHub commits recorded here, not chat summaries. ACK commits are start evidence, not final workpackage completion.

Next gate: consume AG4's independently published immutable terminal evidence and verify completion, identities, child exits and lock release. No disappearance-only takeover, restart, contract change, active raw polling, or automatic deferred dispatch. See `execution/AUTHORITY_COMPATIBILITY.md`. Independent preparation continues while the gate is closed.
