# RTX4080 native calibration plan (no execution authorized)

Use dependent pointer-chase/serialized loads with `clock64`, warmup, working-set/stride sweeps to discover reach boundaries, repeated distributions, data-cache controls, and same-SM/occupancy control where feasible. Separate warm L1, lower-TLB hit, and lower-TLB miss conditions without assuming end-to-end memory plateaus equal pure lookup latency.
