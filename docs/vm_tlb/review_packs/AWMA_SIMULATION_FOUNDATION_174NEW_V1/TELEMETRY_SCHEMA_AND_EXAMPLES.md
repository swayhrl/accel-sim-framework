# Telemetry schema

Required fields: metric_name, metric_value, unit, evidence_origin, scientific_status, claim_scope. Supported namespaces cover TLB, PTW/PWC/walker, L1/L2, DRAM/memory, queues/stalls, performance, and mechanism namespaces. Duplicate rows and unknown namespaces fail closed. Example: tlb.l1.miss, 3, count, HISTORICAL_RECORD, FORMAL, HISTORICAL_REFERENCE.
