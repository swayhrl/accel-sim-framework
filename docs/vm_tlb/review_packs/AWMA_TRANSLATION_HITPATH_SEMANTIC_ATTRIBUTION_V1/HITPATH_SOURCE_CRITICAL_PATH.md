# Source critical path

`shader.cc:2435-2481` selects only `inst.accessq_back()`. If it lacks `vm_translation_applied`, the pipeline calls translation. Any result other than READY increments translation-stall cycles and returns `COAL_STALL`; the back entry is not admitted downstream. `shader.cc:2539-2578` again consumes only accessq_back for ICNT/L1D admission and leaves nonempty queues as COAL_STALL. Thus an untranslated back entry creates head-of-line pre-admission blocking.

`vm_translation.cc:2171-2330` creates/locates a lookup keyed by translation key, stores it in controller inflight state, sets L1 ready after the configured service interval, and has an explicit zero-L1 branch that services lookup in the same cycle and recursively rechecks readiness. The controller owns L1 port accounting (`l1_tlb_ports=1` in effective F0 config); lookup operations can exist in controller inflight state, but shader downstream admission remains one accessq_back at a time.
