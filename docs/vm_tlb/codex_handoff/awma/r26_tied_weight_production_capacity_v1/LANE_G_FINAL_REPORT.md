# Lane G R26 final report

Decision: `R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED`. The integrated component defaults to C1 and exposes S2 only as an explicit capacity opt-in. All B1 one/four/32-step, resume, and policy-switch checks pass.

Measured natural boundaries are C1 B70/B71 and S2 B71/B72 (PASS/OOM). B71 is confirmed C1 OOM 3/3 versus S2 PASS 3/3. Both common-batch timing classes are MIXED. See the review pack for raw group directions, memory, and authority closure.
