# Limitations

This is dependent global-memory timing on an RTX4080, with a register-only timing control. Address spacing is an experiment parameter, not a claimed hardware page size. `cg` is an explicit PTX cache-global load policy variant; it does not isolate TLB latency. The intervening chain is a recorded randomized address-space disturbance, not a TLB flush. No simulator constants are modified.
