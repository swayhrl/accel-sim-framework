# Diagnostic contract

No simulator semantic change or new mechanism was introduced. The formal six points reuse the accepted V1 baseline receipts and existing aggregate VM telemetry. Offline page analysis streams immutable trace payloads and does not feed the simulator.

Existing READY diagnostics are independent opt-in/default-OFF and observational. T0 and T2 diagnostics-OFF replays match the accepted diagnostics-ON scientific signatures exactly. Counters without a time series are not relabeled as histograms, high-water marks, or cycle windows.

No additional ideal point is included: the accepted baseline has no source-identified ideal/near-ideal latency control. The `vm_ideal_translations` accounting counter denotes functional address resolutions and is not an ideal-latency experiment.

Evidence limits:

- requester latency and memory-stage stall counters are aggregate sums, not mutually exclusive critical-path cycles;
- PWQ/walker/lookup occupancy high-water marks are not source-supported by the accepted receipts;
- cycle-window burstiness and per-PC translation stall attribution are unavailable without new telemetry;
- 64KiB is the modeled primary page size; 4KiB results are behavioral support only and are not an RTX4080 page-size claim.
