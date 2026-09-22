# F0 post-parse Segment state

The parsed config has `weight_segmentation_enable=1`, but F0 fair-arm post-parse selection yields runtime `vm_weight_segmentation_enabled=0`, lifecycle `INACTIVE`, zero local table entries and zero functional counters. A descriptor remains loaded (`1`) as legal historical compatibility state, not an active functional path. Source capability is in `vm_translation.cc:1863-1890`; actual F0 runtime state is bound by immutable T0 log.
