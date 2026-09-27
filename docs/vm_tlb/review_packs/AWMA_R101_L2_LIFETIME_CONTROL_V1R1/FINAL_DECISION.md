# Final decision

`R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`

The existing SM89 discard instruction is real and semantically safe at the frozen dead points, but in the qualified L512 pair it removed only 26.26% of NS-family DRAM writes and slowed graph replay. The admitted full A+B persistence-plus-discard control removed no NS-family writes relative to its exact arena baseline and also slowed replay. The remaining issue is GPU-local L2 lifetime control, not a measured Python/host-launch artifact. The precise early-eviction/capacity/granularity contribution remains to be established; no hardware speedup is claimed.

**STOP.** Wait for ChatGPT architecture review. Do not start node174-new, Accel-Sim, a new mechanism, or an untriggered holdout in this Goal.
