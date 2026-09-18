# Probe-time coupling

The model probes TLB state when `ready_cycle=launch+configured_latency` is reached, not at launch. Thus latency controls completion timing and sampling time. This is a model semantic statement, not hardware behavior.
