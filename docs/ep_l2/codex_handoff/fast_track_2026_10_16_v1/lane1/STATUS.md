# Lane1 finite-service producer — first localization checkpoint

New Goal EPL2_FINITE_SERVICE_MICROOPT_PRODUCER_V1 ACTIVE, 2026-10-18T03:02:03Z–07:02:03Z. Authority c8aa87bd sections0–3. Independent candidate Core/Framework branch hrl/ep-l2-finite-service-microopt-lane1-v1; old releases remain frozen. Exact identities and raw evidence: FINITE_SERVICE_MICROOPT_RECEIPT_r1.json.

MQ2 real native cache/Tag/MSHR opportunities reproduce in B16/S64/Unified: actual fill consumes WB bank, head WB waits and second independent read remains queued; recovery preserves WB priority, sectors/UID/lower accept/WAD/P1/drain. MQ2 default-OFF source implemented and syntax checked, NOT yet production runtime tested. A strict plain-LDG decode proof rejects unknown/strong/volatile/acquire/release/async inputs; instructionless reads never bypass.

RG1 now reproduces in actual memory partition queues in all three modes: fill first denies frontend hit write; next cycle older frontend write consumes bank and fills actual one-entry ICNT response FIFO; retained response becomes explicitly unready, ReturnQ same-bank fill ready but services=0. Exact-once versions and full drain pass after relieving backpressure. No arbiter change or benefit claim yet.

Formal candidate build preflight held below50GiB before any CMake/compiler. Small baseline fixture links/syntax checks used canonical leases and bounded output with unchanged48GiB workspace/40GiB Share/64GiB RAM floors. All own leases released; no own daemon/waiter/simulator. No full applications, no RTL changes. Existing frozen H0/combined releases and independent Lane5 accepted evidence are preserved. Next: RG1 bounded ready semantics and actual resource recovery; MQ2 native production validation/release precedes RG1 qualification.
