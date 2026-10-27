# Latency audit: executed CPU scope addendum

This supplements LATENCY_PATH_AUDIT.md and CPU_LATENCY_V2_POINTER_AND_PRESSURE_REVIEW.md without changing their pre-execution evidence or any frozen source/tool. Main compiled and ran V2 under fresh engineering admission; B performed read-only receipt/source-hash and recorded semantic-line checks only. B launched no C++ process.

Main result:
agent_b/engineering_runs/c2a70730-77cc-4a61-b2fd-3139d114a5f1/RESULT.json
SHA2566f6aa864619a0d0a150f1c5b3ea9bc78644660528bdac038abb9309b982b7b38.

B review:
agent_b/CPU_LATENCY_EXECUTED_SCOPE_REVIEW.json
SHA256a3e9e7adbff4191af50d5a2838c2a168262b8f9762b31ac2df8a65cbce252045.

Compile/link rc0, eight CPU execution rc0, four recorded LIFE OFF/ON semantic pairs PASS. Source568dfd/registration743316/plan72d06e match the preserved V2 artifacts. Exact D four configs,32x8,1132:1132:1132:850,simple0,ROP160 and original queues/resources were retained. No production source/main ELF or old build writes; no complete application starts.

## PROVEN on this actual production-linked CPU schedule

| Unloaded read | L0=100 | L1=200 |
|---|---:|---:|
| Delay-queue entry, core counter |166|166|
| Inclusive ready deadline |266|366|
| First eligible actual DRAM edge / MC push |266|367|
| First actual read column, core counter |283|384|
| First read column, DRAM-call ordinal |213|289|
| Response-complete core counter |303|404|

The200 deadline is reached between actual DRAM opportunities, so the packet pushes at367, not366. This is demonstrated DRAM-edge quantization of a CORE-counter threshold. The unloaded completion delta is101core cycles on this schedule; it is not an application-wide additive law.

All four L/mode-case pairs retained exact recorded semantic lines when LIFE changed OFF to ON. B independently checked those selected semantic lines from Main's receipt. B did not independently re-decode the complete non-lifetime raw streams, and the review does not enlarge NI beyond the recorded comparison.

## Actual destination ReturnQ pressure and closure

RETURN_PRESSURE at both L0 and L1 observed real_returnq_full=1 with96actual lower packets/read commands and96exact-once responses. Completion counters were5491 and5592 respectively. All reads drained, max bank grants remained1, and actual public credit_leak_free/resource-closure assertions passed.

This upgrades the former ?96 may fill the64-entry destination queue? from LIKELY to **PROVEN for the executed schedule**. No full assertion was removed and no request count/queue capacity was changed to obtain it.

The resource boundary remains narrow:

- The full queue is the per-subpartition DRAM-to-L2 queue, capacity64.
- The separate internal DRAM returnq has capacity192. This96-read fixture does **not** demonstrate that queue becoming full.
- read_issue_blocked_while_returnq_full was0 in both pressure conditions. The counter counts a live read lower-head issue attempt while the destination return path is full and a general credit is available; it is not the occupancy/full counter. Its zero value does not negate the observed64-entry queue full state. A consistent explanation is that the96packets had already been admitted before that state.
- No general-credit exhaustion, no-return WB progress-credit path, or actual full192-entry DRAM returnq coverage is claimed. n_wr and n_wr_WB were0.
- This proves forward progress and credit closure for the exercised real pressure interval, not every possible downstream blockage or full application.

No additional requests, pressure scan, test execution, application model or budget use was performed for this addendum. The result is CPU engineering evidence only; it does not grant source/application scientific acceptance or predict the matched application's cycles.
