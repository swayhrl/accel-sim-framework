# Telemetry contract

`EPL2M0AV1` is emitted only with `-gpgpu_ep_l2_m0a_stats 1`. The flag is read
only by M0a sampling/printing/counting guards and is absent from admission,
arbitration, scheduling, and resource-transition predicates.

At most once per simulated cycle per physical L2 slice, immediately after
side-effect-free `preview_access()` has formed the exact current frontend-head
admission inputs, M0a increments `m0_frontend_head_observed_cycles`. If
`l2_admission_allowed()` rejects that head, it increments `any_blocked` once.
Independent reason bits are derived from the same preview/input snapshot and
may overlap; they are not a partition and must never be summed.

`tag_way`, WAD, descriptor/MSHR, MissQ, payload-service/data-port, and
response-queue fields correspond to direct preview/admission predicates.
`payload_capacity` and `lowerq` are explicit zero-valued fields in the
corrected D512 frontend contract because neither is a direct frontend
prerequisite. They are not inferred opportunities. Resident occupancy/free is
sampled at the existing frozen B0 point from actual 1024-slot resident state;
the dormant 128-slot bypass store is never used as capacity.

`m0_useful_frontend_admit` increments only after a non-reservation-fail actual
`access()` commit. `m0_useful_response_enqueue` increments immediately before
an actual L2-to-ICNT response queue push. Application rows are cumulative;
kernel rows are shared deltas; 5K rows are exact 64-slice groups. The parser
rejects missing fields, non-64 terminal application cardinality, and partial
5K groups.
