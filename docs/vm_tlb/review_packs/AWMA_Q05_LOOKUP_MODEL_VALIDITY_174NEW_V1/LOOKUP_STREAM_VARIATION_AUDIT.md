# Lookup stream variation

`vm_requests` counts retry/function invocations, whereas `vm_translation_lookup_requests` counts accepted lookup admissions/requesters. Lower latency changes retry/inflight/pending invocation accounting and probe order, so latency points are not fixed-stream additive subtractions.
